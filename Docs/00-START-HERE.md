# Certificate Generator Project - Start Here

## Project Status: 🚀 READY FOR AGENT LAUNCH

**Last Updated**: 2025-07-09  
**Current Phase**: Multi-Agent Setup Complete  
**Overall Progress**: 25%

## Quick Summary

Building a Streamlit-based certificate generator app with:
- Dual authentication (user/admin roles)
- Bulk PDF certificate generation from spreadsheets
- Google Cloud Run deployment
- Template management system

## Current Status

### ✅ Completed
- Project initialization
- Git repository setup
- Directory structure created
- Communication channels established (/tmp/claude-team/)
- Core documentation written (README, CLAUDE.md, PLANNING.md, TASK.md)
- All 5 agent prompts created
- Task distribution file ready (tasks.json)
- Knowledge graph updated

### 🚀 Ready to Launch
- Infrastructure Agent → Terminal 1
- Auth & Admin Agent → Terminal 2  
- PDF Generation Agent → Terminal 3
- Storage & Integration Agent → Terminal 4
- Documentation & Testing Agent → Terminal 5

### 📋 Next Steps
1. Launch all 5 agents using their prompts
2. Monitor progress via /tmp/claude-team/progress.md
3. Watch for blockers in /tmp/claude-team/issues.md
4. Coordinate handoffs via /tmp/claude-team/handoff.md

## Multi-Agent Development Status

| Agent | Status | Progress | Current Task |
|-------|---------|----------|--------------|
| Infrastructure | Not Started | 0% | Waiting to launch |
| Auth & Admin | Not Started | 0% | Waiting to launch |
| PDF Generation | Not Started | 0% | Waiting to launch |
| Storage & Integration | Not Started | 0% | Waiting to launch |
| Documentation & Testing | Not Started | 0% | Waiting to launch |

## Key Files to Review

1. **INITIAL.md** - Original design document
2. **PLANNING.md** - Architecture and implementation plan  
3. **TASK.md** - Current task tracking
4. **CLAUDE.md** - Project-specific AI rules
5. **/tmp/claude-team/** - Real-time agent communication

## Development Workflow

### For New Agents
1. Read this file first
2. Review your assigned tasks in TASK.md
3. Check /tmp/claude-team/handoff.md for dependencies
4. Update /tmp/claude-team/progress.md every 5 minutes
5. Document blockers in /tmp/claude-team/issues.md

### For Integration
1. Monitor all agent progress
2. Coordinate via handoff.md
3. Test components together
4. Update documentation

## Critical Information

### Passwords (Development Only)
```
USER_PASSWORD=UserPass123
ADMIN_PASSWORD=AdminPass456
```

### Key Technologies
- Streamlit 1.31.0+
- PyMuPDF (fitz) 1.23.0+
- Google Cloud Storage
- Docker

### Performance Targets
- < 0.5 sec per certificate
- < 30 sec for 500 certificates
- 40 requests/minute rate limit

## Known Issues
None yet - project just starting

## Recent Changes
- 2025-07-09: Project initialized, multi-agent setup beginning

## Contact for Blockers
Check /tmp/claude-team/issues.md and update with BLOCKING status if you need immediate help.