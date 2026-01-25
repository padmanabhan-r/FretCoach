# FretCoach Documentation

This directory contains the complete documentation for FretCoach, published as GitHub Pages.

## 📚 Documentation Structure

### Getting Started
- **[index.md](index.md)** - Main landing page and navigation hub
- **[introduction.md](introduction.md)** - Why FretCoach exists and how it works
- **[quickstart.md](quickstart.md)** - Get up and running in 5 minutes
- **[judges-start-here.md](judges-start-here.md)** - Essential guide for Comet Opik hackathon reviewers

### System Components
- **[desktop-app.md](desktop-app.md)** - Desktop application deep dive
- **[portable-app.md](portable-app.md)** - Raspberry Pi portable device documentation
- **[web-dashboard.md](web-dashboard.md)** - Web analytics and AI coach platform
- **[audio-analysis-agent-engine.md](audio-analysis-agent-engine.md)** - Real-time audio processing (Fast Loop)
- **[ai-coach-agent-engine.md](ai-coach-agent-engine.md)** - LLM-powered adaptive coaching (Slow Loop)

### Architecture & Technical
- **[architecture.md](architecture.md)** - Overall system design and component interaction
- **[appendix-audio-math.md](appendix-audio-math.md)** - Deep dive into DSP formulas and algorithms

## 🚀 Publishing to GitHub Pages

### Initial Setup

1. **Enable GitHub Pages in repository settings:**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` or `master`
   - Folder: `/docs`
   - Save

2. **Wait for deployment** (usually 1-2 minutes)

3. **Access at:** `https://yourusername.github.io/FretCoach/`

### Updating Documentation

Simply commit and push changes to any `.md` file in this directory. GitHub Actions will automatically rebuild and deploy.

```bash
# Edit documentation
vim docs/introduction.md

# Commit and push
git add docs/
git commit -m "Update documentation"
git push origin main

# GitHub Pages will automatically rebuild in 1-2 minutes
```

## 🎨 Styling

The documentation uses the **Cayman theme** configured in `_config.yml`.

### Custom Styling (Optional)

To customize appearance, create `assets/css/style.scss`:

```scss
---
---

@import "{{ site.theme }}";

// Custom CSS here
```

## 📝 Writing Guidelines

### Markdown Features

**Internal links:**
```markdown
[Quickstart Guide](quickstart.md)
[Desktop App](desktop-app.md)
```

**External links:**
```markdown
[Live Demo](https://fretcoach.online)
[Opik Project](https://comet.com/opik/...)
```

**Code blocks:**
```markdown
```python
def example():
    pass
`` `
```

**Math (KaTeX):**
```markdown
Inline: $E = mc^2$

Block:
$$
f(x) = \int_{-\infty}^{\infty} e^{-x^2} dx
$$
```

**Tables:**
```markdown
| Metric | Description |
|--------|-------------|
| Pitch  | Accuracy    |
| Timing | Stability   |
```

### Style Guidelines

1. **Clear headings** - Use hierarchical structure (H1 → H2 → H3)
2. **Short paragraphs** - 2-4 sentences maximum
3. **Code examples** - Include practical, runnable code
4. **Diagrams** - Use ASCII art for simple architecture diagrams
5. **Concise** - No fluff, get to the point

### Navigation

Each page should have navigation links at the bottom:

```markdown
---

**Navigation:**
- [← Previous Page](previous.md)
- [Next Page →](next.md)
- [Back to Index](index.md)
```

## 🔍 Testing Locally

### With Jekyll (Recommended)

```bash
# Install Jekyll (macOS)
brew install ruby
gem install bundler jekyll

# Navigate to docs
cd docs

# Create Gemfile
cat > Gemfile << 'EOF'
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "webrick"
EOF

# Install dependencies
bundle install

# Serve locally
bundle exec jekyll serve

# Visit http://localhost:4000
```

### With Python (Simple)

```bash
# Navigate to docs
cd docs

# Serve with Python
python3 -m http.server 8000

# Visit http://localhost:8000
# Note: This won't render Jekyll templates, just raw markdown
```

## 📊 Documentation Status

| Document | Status | Notes |
|----------|--------|-------|
| index.md | ✅ Complete | Landing page, navigation, tech stack |
| introduction.md | ✅ Complete | Overview, problem statement, ecosystem |
| quickstart.md | ✅ Complete | Setup guide, first session walkthrough |
| judges-start-here.md | ✅ Complete | Demo guide, Opik integration, evaluation |
| desktop-app.md | ✅ Complete | Desktop application deep dive |
| portable-app.md | ✅ Complete | Raspberry Pi device documentation |
| web-dashboard.md | ✅ Complete | Web analytics and AI coach platform |
| architecture.md | ✅ Complete | System architecture, components, database |
| audio-analysis-agent-engine.md | ✅ Complete | Real-time audio processing engine |
| ai-coach-agent-engine.md | ✅ Complete | AI coaching system, LLM integration |
| appendix-audio-math.md | ✅ Complete | DSP mathematics, formulas, algorithms |
| README.md | ✅ Complete | Documentation structure and publishing guide |

## 🎯 For Hackathon Judges

If you're reviewing this project for the Comet Opik hackathon:

→ **Start here:** [judges-start-here.md](judges-start-here.md)

This guide provides:
- Quick demo walkthrough
- Opik integration highlights
- Key evaluation points
- Direct links to trace data

## 📞 Contact

Questions or issues with the documentation?
- Open an issue in the GitHub repository
- Check [fretcoach.online](https://fretcoach.online) for live demos

---

**Last Updated:** January 2026
