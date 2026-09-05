# Project scaffold file
# ============================================================
# AI Resume Screening & Interview System
# Frontend Dockerfile
# ============================================================

FROM nginx:1.27-alpine

# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

LABEL maintainer="AI Resume Screening System"
LABEL description="Frontend for AI Resume Screening & Interview System"

# ------------------------------------------------------------
# Remove default Nginx website
# ------------------------------------------------------------

RUN rm -rf /usr/share/nginx/html/*

# ------------------------------------------------------------
# Copy frontend application
# ------------------------------------------------------------

COPY frontend/index.html /usr/share/nginx/html/

COPY frontend/css /usr/share/nginx/html/css
COPY frontend/js /usr/share/nginx/html/js
COPY frontend/components /usr/share/nginx/html/components
COPY frontend/pages /usr/share/nginx/html/pages
COPY frontend/services /usr/share/nginx/html/services
COPY frontend/charts /usr/share/nginx/html/charts
COPY frontend/assets /usr/share/nginx/html/assets
COPY frontend/pages-html /usr/share/nginx/html/pages-html

# ------------------------------------------------------------
# Optional favicon
# ------------------------------------------------------------

COPY frontend/favicon.ico /usr/share/nginx/html/favicon.ico

# ------------------------------------------------------------
# Nginx configuration
# ------------------------------------------------------------

COPY infrastructure/nginx/frontend.conf /etc/nginx/conf.d/default.conf

# ------------------------------------------------------------
# Permissions
# ------------------------------------------------------------

RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# ------------------------------------------------------------
# Port
# ------------------------------------------------------------

EXPOSE 80

# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------

HEALTHCHECK --interval=30s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD wget --no-verbose \
    --tries=1 \
    --spider \
    http://localhost/ || exit 1

# ------------------------------------------------------------
# Start Nginx
# ------------------------------------------------------------

CMD ["nginx", "-g", "daemon off;"]