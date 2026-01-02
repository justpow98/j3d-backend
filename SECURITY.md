# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in J3D Backend, **please do NOT open a public issue**. Instead:

1. **Email**: Send a detailed report to the project maintainer with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if applicable)

2. **Response Timeline**: We will acknowledge receipt within 48 hours and provide an estimated fix timeline

3. **Responsible Disclosure**: Please allow 30 days for a fix before any public disclosure

## Supported Versions

| Version | Status | Security Updates |
|---------|--------|------------------|
| 2.0.x   | Active | Yes              |
| 1.x.x   | EOL    | No               |

Only the latest minor version receives security updates.

## Security Practices

### Authentication & Authorization
- OAuth 2.0 integration with Etsy API
- JWT/session-based authentication for API clients
- Role-based access control (RBAC) for API endpoints
- Secure password hashing with bcrypt (if user accounts used)
- Authentication required for all protected endpoints

### Database Security
- PostgreSQL with encrypted connections (SSL/TLS)
- Database user with minimal required permissions
- No database credentials in source code
- Parameterized queries to prevent SQL injection
- Regular database backups with encryption

### API Security
- Input validation and sanitization on all endpoints
- Rate limiting to prevent brute-force attacks
- CORS properly configured
- HTTPS enforced in production
- Request/response logging (without sensitive data)
- API versioning to manage breaking changes securely

### Secret Management
- `.env` file excluded from git via `.gitignore`
- `.env.example` provided as template with placeholders
- All secrets loaded from environment variables
- No hardcoded credentials or API keys
- Secrets rotated regularly
- Database passwords stored securely

### Dependency Management
- Regular `pip` dependency updates
- Security vulnerability scanning with `pip audit` or similar
- Flask security patches applied promptly
- Python version kept up-to-date
- Automated dependency checks in CI/CD pipeline

### Code Security
- Input validation on all API endpoints
- Output encoding to prevent injection attacks
- Error handling that doesn't expose system details
- Logging of security events
- No debug mode in production
- Static code analysis tools integrated

### Etsy API Integration
- OAuth tokens stored securely (database with encryption)
- Token refresh handled securely
- API credentials never logged
- Etsy API errors handled without exposing internals
- Rate limiting respected for Etsy API calls

### Container Security
- Non-root user (`appuser`) runs the application
- Multi-stage Docker builds for minimal image size
- Only necessary packages in final image
- Read-only filesystem where possible
- Container health checks enabled
- No privileged mode execution

### Encryption
- Database connections use TLS
- Sensitive data encrypted at rest in database
- API communication over HTTPS
- OAuth tokens encrypted in database

## Known Security Considerations

1. **CORS Configuration**: Ensure CORS is limited to known frontend domains only
2. **API Rate Limiting**: Implement per-IP and per-user rate limiting
3. **Database Access**: Restrict database network access to application server only
4. **File Uploads**: If enabled, validate file types and scan for malware
5. **Etsy API Keys**: Rotate regularly and monitor for unauthorized access
6. **Session Management**: Implement session timeout and regeneration after login

## Security Recommendations for Deployment

### Environment Variables
Set these securely in your deployment environment:
```
DATABASE_URL=postgresql://user:pass@db-host:5432/j3d
SECRET_KEY=<generate-strong-random-key>
FLASK_CONFIG=production
ETSY_CLIENT_ID=<your-etsy-app-id>
ETSY_CLIENT_SECRET=<your-etsy-app-secret>
ETSY_REDIRECT_URI=https://your-domain.com/oauth-callback
```

Never commit `.env` file with real values.

### HTTPS/TLS
- Always use HTTPS in production
- Use valid SSL/TLS certificates (Let's Encrypt recommended)
- Enforce HTTPS redirects via middleware
- Use HSTS with `max-age=31536000` or higher

### Database Security
- Use strong, unique passwords for database user
- Limit database access to application server only
- Enable PostgreSQL SSL/TLS
- Regular encrypted backups
- Monitor database logs for suspicious activity
- Keep PostgreSQL updated

### API Security Headers
- `Content-Type: application/json` enforced
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security` header enabled
- `Content-Security-Policy` appropriate for API

### Container Deployment
- Run with resource limits (memory, CPU)
- Mount `/tmp` as tmpfs for temporary files
- Use read-only root filesystem
- No privileged mode
- Health checks configured
- Container logs monitored

### Network Security
- Restrict API access to known frontend IPs if possible
- Use private networks for backend communication
- Database not exposed to internet
- Implement DDoS protection
- Monitor for suspicious access patterns
- Use VPC/security groups for network isolation

### Logging & Monitoring
- Log all authentication attempts
- Log API errors and exceptions
- Monitor for repeated failed login attempts
- Alert on unusual database activity
- No sensitive data logged (passwords, tokens, etc.)
- Centralize logs for security analysis

## API Security Checklist

- [ ] All endpoints validate input
- [ ] HTTPS enforced in production
- [ ] CORS restricted to known domains
- [ ] Rate limiting implemented
- [ ] Authentication required for protected endpoints
- [ ] Database credentials in environment variables only
- [ ] Error messages don't expose system details
- [ ] Logging excludes sensitive data
- [ ] Dependencies regularly updated
- [ ] Etsy API credentials secured
- [ ] Database access restricted to app server
- [ ] Health checks don't expose system information

## Incident Response

If a security vulnerability is discovered:

1. **Immediate**: Patch is developed in private branch
2. **Testing**: Security patch tested against vulnerability
3. **Within 7 days**: Security release published
4. **Communication**: Security advisory issued to users
5. **Follow-up**: Post-incident analysis and preventive measures

## Security Scanning

This project includes:
- Python dependency vulnerability scanning
- Container image scanning for base image vulnerabilities
- Code static analysis where applicable
- Regular security audits of critical components

## Deployment Security Checklist

- [ ] HTTPS/TLS enabled with valid certificates
- [ ] All environment variables set securely
- [ ] .env file NOT in repository
- [ ] Database credentials strong and unique
- [ ] CORS configured for your frontend only
- [ ] API rate limiting enabled
- [ ] Container runs as non-root user
- [ ] Database access restricted to app server
- [ ] Monitoring and alerting configured
- [ ] Regular automated backups enabled
- [ ] Secrets rotation schedule established
- [ ] Etsy API credentials secured and rotated

## Contact

For security concerns, contact the project maintainer directly rather than using public issue trackers.

---

**Last Updated**: January 2, 2026
