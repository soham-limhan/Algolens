# AlgoLens multi-language sandbox base image (Java, Python, C++, C, JavaScript)
# Built once, reused across all submissions and benchmark runs.
FROM eclipse-temurin:21-jdk-alpine

# Install Python 3, GCC, G++, Node.js, and C runtime headers
RUN apk add --no-cache \
    python3 \
    gcc \
    g++ \
    musl-dev \
    nodejs

# Create a non-root user for running submissions
RUN addgroup -S sandbox && adduser -S sandbox -G sandbox

# Writable scratch area & class mount directory
RUN mkdir -p /sandbox/scratch /sandbox/classes && chown -R sandbox:sandbox /sandbox

WORKDIR /sandbox

USER sandbox
