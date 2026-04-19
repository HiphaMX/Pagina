# Webflow Design Methodology

To ensure code exported by DesignFlow is 100% compatible and easy to manage in Webflow:

## 1. Class Naming (BEM-ish)
- Use descriptive, Webflow-friendly class names.
- Example: `hero-section`, `glass-card`, `btn-primary`.
- Avoid auto-generated or cryptic names.

## 2. CSS Architecture
- Use **CSS Variables** (`:root`) if possible, but keep a fallback for Webflow's visual editor.
- Store project-specific variables in `projects/[PROJECT]/branding.md`.
- Prefer Flexbox and Grid.

## 3. Webflow-Specific Optimizations
- **Embeds**: Keep code blocks modular so they can be pasted into a Webflow "Embed" component.
- **Backgrounds**: Use CSS for gradients and glassmorphism to reduce image assets.
- **Images**: Use relative paths or placeholders during development, but define them clearly for the user to replace with Webflow CDN links.

## 4. UX Best Practices
- **Mobile First**: All designs must be responsive.
- **Accessibility**: Ensure high contrast and semantic tags (h1-h6, section, nav).
- **Interactions**: Use standard CSS transitions that mirrors Webflow's interaction engine.
