import { useState, useEffect, useCallback, useRef } from "react";
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../api/client';
import styles from './Forum.module.css';

const CATEGORIES = ["All", "General", "Algorithms", "Questions", "Contest", "Feedback"];

/**
 * Render text content with @username mentions styled with highlight tags.
 */
function renderContentWithMentions(text) {
  if (!text) return "";
  // Split on @username patterns
  const parts = text.split(/(@[a-zA-Z0-9_ -]+(?:\s|$|[.,!?]))/g);
  return parts.map((part, i) => {
    if (part.startsWith("@")) {
      const trimmed = part.trim();
      // Extract punctuation if trailing
      const punctMatch = trimmed.match(/([.,!?]+)$/);
      const punct = punctMatch ? punctMatch[1] : "";
      const handle = punct ? trimmed.slice(0, -punct.length) : trimmed;
      return (
        <span key={i}>
          <span className={styles.mentionTag}>{handle}</span>
          {punct}
          {part.endsWith(" ") ? " " : ""}
        </span>
      );
    }
    return part;
  });
}

/**
 * Reusable Mention Textarea with autocomplete suggestions for @username.
 */
function MentionTextarea({ value, onChange, placeholder, style, required, textareaRef }) {
  const [mentionQuery, setMentionQuery] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [activeIdx, setActiveIdx] = useState(0);
  const [cursorPos, setCursorPos] = useState(0);
  const localRef = useRef(null);
  const ref = textareaRef || localRef;

  // Detect @mention trigger when typing
  const handleInput = (e) => {
    const val = e.target.value;
    const pos = e.target.selectionStart;
    setCursorPos(pos);
    onChange(val);

    const beforeCursor = val.slice(0, pos);
    const match = beforeCursor.match(/@([a-zA-Z0-9_]*)$/);
    if (match) {
      setMentionQuery(match[1]);
      setActiveIdx(0);
    } else {
      setMentionQuery(null);
      setSuggestions([]);
    }
  };

  // Fetch users when mentionQuery changes
  useEffect(() => {
    if (mentionQuery === null) return;
    let isCurrent = true;
    api.get('/forum/users/mentions', { params: { q: mentionQuery } })
      .then(r => {
        if (isCurrent) {
          setSuggestions(r.data || []);
        }
      })
      .catch(() => {
        if (isCurrent) setSuggestions([]);
      });
    return () => { isCurrent = false; };
  }, [mentionQuery]);

  const insertMention = (userName) => {
    const beforeCursor = value.slice(0, cursorPos);
    const afterCursor = value.slice(cursorPos);
    const mentionPrefixMatch = beforeCursor.match(/@([a-zA-Z0-9_]*)$/);
    if (!mentionPrefixMatch) return;

    const replaceStart = mentionPrefixMatch.index;
    const nextVal = beforeCursor.slice(0, replaceStart) + `@${userName} ` + afterCursor;
    onChange(nextVal);
    setMentionQuery(null);
    setSuggestions([]);

    setTimeout(() => {
      if (ref.current) {
        ref.current.focus();
        const newPos = replaceStart + userName.length + 2;
        ref.current.setSelectionRange(newPos, newPos);
      }
    }, 10);
  };

  const handleKeyDown = (e) => {
    if (mentionQuery !== null && suggestions.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActiveIdx(prev => (prev + 1) % suggestions.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActiveIdx(prev => (prev - 1 + suggestions.length) % suggestions.length);
      } else if (e.key === "Enter" || e.key === "Tab") {
        if (suggestions[activeIdx]) {
          e.preventDefault();
          insertMention(suggestions[activeIdx].name);
        }
      } else if (e.key === "Escape") {
        setMentionQuery(null);
        setSuggestions([]);
      }
    }
  };

  return (
    <div className={styles.textareaContainer}>
      <textarea
        ref={ref}
        className={styles.textarea}
        placeholder={placeholder}
        value={value}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        onKeyUp={(e) => setCursorPos(e.target.selectionStart)}
        onClick={(e) => setCursorPos(e.target.selectionStart)}
        style={style}
        required={required}
      />

      {mentionQuery !== null && suggestions.length > 0 && (
        <div className={styles.mentionDropdown}>
          <div className={styles.mentionDropdownHeader}>
            Tag User (@)
          </div>
          {suggestions.map((u, i) => (
            <div
              key={u.id || i}
              className={`${styles.mentionItem} ${i === activeIdx ? styles.mentionItemActive : ""}`}
              onMouseDown={(e) => {
                e.preventDefault();
                insertMention(u.name);
              }}
              onMouseEnter={() => setActiveIdx(i)}
            >
              <div className={styles.mentionAvatar}>
                {u.name.charAt(0).toUpperCase()}
              </div>
              <span>{u.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Recursive Reply Item component for threaded / nested discussions.
 */
function ReplyCard({ reply, onReplyTo, formatDate, user }) {
  return (
    <div className={reply.parent_id ? styles.nestedCommentCard : styles.commentCard}>
      <div className={styles.commentHeader}>
        <div className={styles.commentAuthorGroup}>
          <span className={styles.commentAuthor}>@{reply.author}</span>
          {reply.parent_author && (
            <span className={styles.replyToBadge}>
              replying to <strong>@{reply.parent_author}</strong>
            </span>
          )}
        </div>
        <span style={{ fontSize: "0.8rem", color: "var(--text-dim)" }}>
          {formatDate(reply.created_at || reply.createdAt)}
        </span>
      </div>

      <div className={styles.commentBody}>
        {renderContentWithMentions(reply.content)}
      </div>

      {user && (
        <div className={styles.commentFooter}>
          <button
            type="button"
            className={styles.replyBtn}
            onClick={() => onReplyTo(reply)}
            title={`Reply to @${reply.author}`}
          >
            💬 Reply
          </button>
        </div>
      )}

      {/* Render Nested Children Replies if any */}
      {reply.children && reply.children.length > 0 && (
        <div className={styles.nestedReplies}>
          {reply.children.map(child => (
            <ReplyCard
              key={child.id}
              reply={child}
              onReplyTo={onReplyTo}
              formatDate={formatDate}
              user={user}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Forum() {
  const { user } = useAuth();

  // ── States ────────────────────────────────────────────────────────────────
  const [threads, setThreads] = useState([]);
  const [currentThreadDetail, setCurrentThreadDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  const [activeCategory, setActiveCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("newest"); // "newest" | "popular"

  // Navigation / View state: "list" | "detail" | "create"
  const [view, setView] = useState("list");
  const [selectedThreadId, setSelectedThreadId] = useState(null);

  // Form states
  const [newTitle, setNewTitle] = useState("");
  const [newCategory, setNewCategory] = useState("General");
  const [newContent, setNewContent] = useState("");
  const [formError, setFormError] = useState("");

  // Comment state & replyingTo state
  const [newComment, setNewComment] = useState("");
  const [replyingTo, setReplyingTo] = useState(null); // { id, author }
  const commentInputRef = useRef(null);

  // ── API Fetchers ──────────────────────────────────────────────────────────
  const fetchThreads = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/forum/threads', {
        params: {
          category: activeCategory,
          search: searchQuery,
          sort_by: sortBy,
        },
      });
      setThreads(data);
    } catch (err) {
      console.error("Failed to fetch threads:", err);
    } finally {
      setLoading(false);
    }
  }, [activeCategory, searchQuery, sortBy]);

  const fetchThreadDetail = useCallback(async (threadId) => {
    setLoading(true);
    try {
      const { data } = await api.get(`/forum/threads/${threadId}`);
      setCurrentThreadDetail(data);
    } catch (err) {
      console.error("Failed to fetch thread detail:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (view === "list") {
      fetchThreads();
    } else if (view === "detail" && selectedThreadId) {
      fetchThreadDetail(selectedThreadId);
    }
  }, [view, selectedThreadId, fetchThreads, fetchThreadDetail]);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleLike = async (threadId, e) => {
    e.stopPropagation(); // Prevent clicking card
    if (!user) {
      alert("Please sign in or register to like threads!");
      return;
    }

    try {
      const { data } = await api.post(`/forum/threads/${threadId}/like`);

      setThreads(prev => prev.map(t => (t.id === threadId ? data : t)));
      if (currentThreadDetail && currentThreadDetail.id === threadId) {
        setCurrentThreadDetail(prev => ({
          ...prev,
          likes: data.likes,
          liked_by: data.liked_by,
        }));
      }
    } catch (err) {
      console.error("Failed to like thread:", err);
    }
  };

  const handleCreateThread = async (e) => {
    e.preventDefault();
    if (!user) {
      setFormError("You must be logged in to create a thread.");
      return;
    }
    if (!newTitle.trim() || !newContent.trim()) {
      setFormError("Title and content cannot be empty.");
      return;
    }

    try {
      const { data } = await api.post('/forum/threads', {
        title: newTitle.trim(),
        category: newCategory,
        content: newContent.trim(),
      });

      // Reset form
      setNewTitle("");
      setNewCategory("General");
      setNewContent("");
      setFormError("");

      // Open new thread
      setSelectedThreadId(data.id);
      setView("detail");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setFormError(Array.isArray(detail) ? detail[0]?.message : (detail || "Failed to create thread"));
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!user || !newComment.trim() || !selectedThreadId) return;

    try {
      const { data } = await api.post(`/forum/threads/${selectedThreadId}/replies`, {
        content: newComment.trim(),
        parent_id: replyingTo?.id || null,
      });

      if (currentThreadDetail) {
        setCurrentThreadDetail(prev => ({
          ...prev,
          replies: [...(prev.replies || []), data],
        }));
      }

      setNewComment("");
      setReplyingTo(null);
    } catch (err) {
      console.error("Failed to add reply:", err);
    }
  };

  const handleStartReply = (reply) => {
    setReplyingTo({ id: reply.id, author: reply.author });
    // Pre-populate @username mention if not already there
    if (!newComment.startsWith(`@${reply.author}`)) {
      setNewComment(`@${reply.author} `);
    }
    if (commentInputRef.current) {
      commentInputRef.current.focus();
      commentInputRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  // ── Helper ────────────────────────────────────────────────────────────────
  const formatDate = (isoString) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  // Build tree of replies (root replies with recursive children)
  const structuredReplies = (() => {
    const rawReplies = currentThreadDetail?.replies || [];
    const replyMap = {};
    const roots = [];

    rawReplies.forEach(r => {
      replyMap[r.id] = { ...r, children: [] };
    });

    rawReplies.forEach(r => {
      if (r.parent_id && replyMap[r.parent_id]) {
        replyMap[r.parent_id].children.push(replyMap[r.id]);
      } else {
        roots.push(replyMap[r.id]);
      }
    });

    return roots;
  })();

  // ── Renders ───────────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>

      {/* ── HEADER ──────────────────────────────────────────────────────── */}
      {view === "list" && (
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>Developer Forum</h1>
            <p className={styles.sub}>Discuss problem strategies, algorithms, and share feedback</p>
          </div>
          {user ? (
            <button className="btn btn-primary" onClick={() => setView("create")}>
              + New Topic
            </button>
          ) : (
            <Link to="/login" className="btn btn-secondary">
              Login to post
            </Link>
          )}
        </div>
      )}

      {/* ── LIST VIEW ───────────────────────────────────────────────────── */}
      {view === "list" && (
        <>
          <div className={styles.controls}>
            <div className={styles.searchAndSort}>
              <div className={styles.searchWrapper}>
                <span className={styles.searchIcon}>🔍</span>
                <input
                  type="text"
                  placeholder="Search topics or content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={styles.searchInput}
                />
              </div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className={styles.selectInput}
              >
                <option value="newest">Sort by: Newest</option>
                <option value="popular">Sort by: Upvotes</option>
              </select>
            </div>

            <div className={styles.categories}>
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`${styles.categoryTab} ${activeCategory === cat ? styles.categoryTabActive : ""}`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.threadList}>
            {loading ? (
              <div style={{ textAlign: "center", padding: "3rem" }}>
                <span className="spinner" />
              </div>
            ) : threads.length === 0 ? (
              <div className={styles.emptyState}>
                <div className={styles.emptyStateIcon}>💬</div>
                <h3>No threads found</h3>
                <p>Be the first to start a conversation in this category!</p>
              </div>
            ) : (
              threads.map(t => {
                const likedByList = t.liked_by || t.likedBy || [];
                const userLiked = user && likedByList.includes(user.id);
                const replyCount = t.replies_count ?? t.replies?.length ?? 0;

                return (
                  <div
                    key={t.id}
                    className={styles.threadCard}
                    onClick={() => {
                      setSelectedThreadId(t.id);
                      setView("detail");
                    }}
                  >
                    <div className={styles.threadCardHeader}>
                      <span className={styles.categoryBadge}>{t.category}</span>
                      <span className={styles.authorMeta}>
                        Posted by <strong>{t.author}</strong> • {formatDate(t.created_at || t.createdAt)}
                      </span>
                    </div>

                    <h2 className={styles.threadTitle}>{t.title}</h2>
                    <p className={styles.threadSnippet}>{t.content}</p>

                    <div className={styles.threadCardFooter}>
                      <div className={styles.stats}>
                        <button
                          className={`${styles.voteButton} ${userLiked ? styles.voted : ""}`}
                          onClick={(e) => handleLike(t.id, e)}
                        >
                          ▲ {t.likes}
                        </button>
                        <span className={styles.statItem}>
                          💬 {replyCount} replies
                        </span>
                      </div>
                      <span style={{ fontSize: "0.85rem", color: "var(--accent-light)" }}>
                        Read Thread →
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </>
      )}

      {/* ── DETAIL VIEW ─────────────────────────────────────────────────── */}
      {view === "detail" && (
        loading && !currentThreadDetail ? (
          <div style={{ textAlign: "center", padding: "4rem" }}><span className="spinner" /></div>
        ) : currentThreadDetail ? (
          <div>
            <button
              className="btn btn-secondary backButton"
              style={{ marginBottom: "1.5rem" }}
              onClick={() => {
                setView("list");
                setReplyingTo(null);
                setNewComment("");
              }}
            >
              ← Back to Forum
            </button>

            <div className={styles.detailCard}>
              <div className={styles.detailHeader}>
                <div className={styles.detailMeta}>
                  <span className={styles.categoryBadge}>{currentThreadDetail.category}</span>
                  <span className={styles.authorMeta}>
                    Started by <strong>{currentThreadDetail.author}</strong> • {formatDate(currentThreadDetail.created_at || currentThreadDetail.createdAt)}
                  </span>
                </div>
                <h1 className={styles.detailTitle}>{currentThreadDetail.title}</h1>
              </div>

              <div className={styles.detailBody}>
                {renderContentWithMentions(currentThreadDetail.content)}
              </div>

              <div className={styles.detailActions}>
                <button
                  className={`${styles.voteButton} ${(user && (currentThreadDetail.liked_by || []).includes(user.id)) ? styles.voted : ""}`}
                  onClick={(e) => handleLike(currentThreadDetail.id, e)}
                >
                  ▲ {currentThreadDetail.likes} Upvote
                </button>
                <span className={styles.authorMeta}>
                  {(currentThreadDetail.replies || []).length} replies
                </span>
              </div>
            </div>

            <div className={styles.commentsSection}>
              <h3 className={styles.sectionTitle}>
                <span>💬</span> Replies ({(currentThreadDetail.replies || []).length})
              </h3>

              <div className={styles.commentList}>
                {structuredReplies.length === 0 ? (
                  <p style={{ color: "var(--text-dim)", fontSize: "0.95rem" }}>
                    No replies yet. Be the first to share your thoughts!
                  </p>
                ) : (
                  structuredReplies.map(r => (
                    <ReplyCard
                      key={r.id}
                      reply={r}
                      onReplyTo={handleStartReply}
                      formatDate={formatDate}
                      user={user}
                    />
                  ))
                )}
              </div>

              {user ? (
                <form onSubmit={handleAddComment} className={styles.replyForm}>
                  <h4 style={{ marginBottom: "0.75rem", fontWeight: 600 }}>
                    {replyingTo ? "Leave a Reply" : "Post a Reply"}
                  </h4>

                  {replyingTo && (
                    <div className={styles.replyingBanner}>
                      <span>
                        Replying to <strong>@{replyingTo.author}</strong>
                      </span>
                      <button
                        type="button"
                        className={styles.cancelReplyBtn}
                        onClick={() => {
                          setReplyingTo(null);
                          if (newComment.startsWith(`@${replyingTo.author}`)) {
                            setNewComment(newComment.replace(new RegExp(`^@${replyingTo.author}\\s*`), ""));
                          }
                        }}
                      >
                        ✕ Cancel
                      </button>
                    </div>
                  )}

                  <MentionTextarea
                    textareaRef={commentInputRef}
                    placeholder="Write your response... Type @ to tag a member. Markdown supported."
                    value={newComment}
                    onChange={setNewComment}
                    required
                  />

                  <button type="submit" className="btn btn-primary">
                    {replyingTo ? "Submit Reply" : "Post Reply"}
                  </button>
                </form>
              ) : (
                <div className={styles.loginPrompt}>
                  Please <Link to="/login" className={styles.loginLink}>log in</Link> to share your response.
                </div>
              )}
            </div>
          </div>
        ) : (
          <div>
            <button className="btn btn-secondary backButton" onClick={() => setView("list")}>← Back to Forum</button>
            <p style={{ marginTop: "1rem" }}>Thread not found.</p>
          </div>
        )
      )}

      {/* ── CREATE VIEW ─────────────────────────────────────────────────── */}
      {view === "create" && (
        <div>
          <button
            className="btn btn-secondary backButton"
            style={{ marginBottom: "1.5rem" }}
            onClick={() => setView("list")}
          >
            Cancel
          </button>

          <div className={styles.formCard}>
            <h2 style={{ marginBottom: "1.5rem", fontWeight: 700 }}>Start a New Topic</h2>

            {formError && <div className={styles.error}>{formError}</div>}

            <form onSubmit={handleCreateThread}>
              <div className={styles.formGroup}>
                <label className={styles.label}>Topic Title</label>
                <input
                  type="text"
                  placeholder="What is your topic about?"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className={styles.input}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className={styles.selectInput}
                  style={{ width: "fit-content" }}
                >
                  {CATEGORIES.filter(c => c !== "All").map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Content</label>
                <MentionTextarea
                  placeholder="Describe your question, idea or details... Type @ to mention a user."
                  value={newContent}
                  onChange={setNewContent}
                  style={{ minHeight: "200px" }}
                  required
                />
              </div>

              <div className={styles.formActions}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setView("list")}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Publish Topic
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}