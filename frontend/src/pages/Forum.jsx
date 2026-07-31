import { useState, useEffect, useCallback } from "react";
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../api/client';
import styles from './Forum.module.css';

const CATEGORIES = ["All", "General", "Algorithms", "Questions", "Contest", "Feedback"];

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

  // Comment state
  const [newComment, setNewComment] = useState("");

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
      });

      if (currentThreadDetail) {
        setCurrentThreadDetail(prev => ({
          ...prev,
          replies: [...(prev.replies || []), data],
        }));
      }

      setNewComment("");
    } catch (err) {
      console.error("Failed to add reply:", err);
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
              onClick={() => setView("list")}
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
                {currentThreadDetail.content}
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
                {(currentThreadDetail.replies || []).map(r => (
                  <div key={r.id} className={styles.commentCard}>
                    <div className={styles.commentMeta}>
                      <span className={styles.commentAuthor}>@{r.author}</span>
                      <span>{formatDate(r.created_at || r.createdAt)}</span>
                    </div>
                    <div className={styles.commentBody}>{r.content}</div>
                  </div>
                ))}
              </div>

              {user ? (
                <form onSubmit={handleAddComment} className={styles.replyForm}>
                  <h4 style={{ marginBottom: "0.75rem", fontWeight: 600 }}>Post a Reply</h4>
                  <textarea
                    className={styles.textarea}
                    placeholder="Write your response... Markdown formatting supported."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    required
                  />
                  <button type="submit" className="btn btn-primary">
                    Post Reply
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
                <textarea
                  placeholder="Describe your question, idea or details..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  className={styles.textarea}
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