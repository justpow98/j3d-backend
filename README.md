# j3d-backend

![Docker Build](https://github.com/justpow98/j3d-backend/actions/workflows/docker-build.yml/badge.svg)
![Docker Image Size](https://ghcr-badge.egpl.dev/justpow98/j3d-backend/size)
![Docker Image Version](https://ghcr-badge.egpl.dev/justpow98/j3d-backend/tags)

Backend for my company app.

## 🐳 Docker

Pull and run the latest image:
```bash
docker pull ghcr.io/justpow98/j3d-backend:latest
docker run -d -p 5000:5000 --env-file .env ghcr.io/justpow98/j3d-backend:latest
```

Or use Docker Compose:
```bash
docker-compose up -d
```

## 📦 Available Images

- `ghcr.io/justpow98/j3d-backend:latest` - Latest main branch build
- `ghcr.io/justpow98/j3d-backend:main` - Main branch
- `ghcr.io/justpow98/j3d-backend:main-<sha>` - Specific commit

---

**Note:** Replace `justpow98` and `j3d-backend` with your actual GitHub username and repository name.