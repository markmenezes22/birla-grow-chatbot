---
name: Luminous Fintech
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#b9caca'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#849495'
  outline-variant: '#3a494a'
  surface-tint: '#00dce5'
  primary: '#e9feff'
  on-primary: '#003739'
  primary-container: '#00f5ff'
  on-primary-container: '#006c71'
  inverse-primary: '#00696e'
  secondary: '#dfb7ff'
  on-secondary: '#4b007e'
  secondary-container: '#9d05ff'
  on-secondary-container: '#f7e6ff'
  tertiary: '#fff9f0'
  on-tertiary: '#3a3000'
  tertiary-container: '#ffdb40'
  on-tertiary-container: '#736000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#63f7ff'
  primary-fixed-dim: '#00dce5'
  on-primary-fixed: '#002021'
  on-primary-fixed-variant: '#004f53'
  secondary-fixed: '#f1daff'
  secondary-fixed-dim: '#dfb7ff'
  on-secondary-fixed: '#2d004f'
  on-secondary-fixed-variant: '#6b00b0'
  tertiary-fixed: '#ffe16d'
  tertiary-fixed-dim: '#e9c400'
  on-tertiary-fixed: '#221b00'
  on-tertiary-fixed-variant: '#544600'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  title-md:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

This design system is engineered for a premium, high-tech financial intelligence experience. The brand personality is authoritative yet visionary, combining the stability of traditional finance with the speed of decentralized technology. The target audience consists of sophisticated investors and tech-native users who demand clarity and cutting-edge aesthetics.

The visual style is a fusion of **Glassmorphism** and **High-Contrast Dark Mode**. It utilizes deep, layered backgrounds to create a sense of infinite depth, while vibrant neon accents serve as directional light sources. Every interface element should feel like a physical piece of illuminated glass floating in a structured digital space. The emotional response should be one of "controlled power"—precise, secure, and futuristic.

## Colors

The palette is anchored in a multi-layered dark theme. The base layer uses **Deep Midnight Blue (#0B0F19)** for primary backgrounds, while **Charcoal (#121826)** defines elevated containers and surface areas.

Interactive and semantic highlights are driven by a high-energy trio:
- **Cyan (#00F5FF):** Used for primary actions, success states, and growth indicators.
- **Neon Purple (#9D00FF):** Used for AI-driven features, chatbot interactions, and secondary accents.
- **Electric Gold (#FFD700):** Reserved for premium tiers, alerts, and high-value data points.

Gradients should be used sparingly but impactfully, typically transitioning from Cyan to Purple at a 135-degree angle to signify active processing or transitions.

## Typography

The system utilizes a dual-font strategy to balance character with utility. **Outfit** is the primary display face, providing a modern, geometric feel for headlines and titles. **Inter** is employed for all body copy and financial data to ensure maximum legibility at small sizes. **JetBrains Mono** is introduced for labels and technical data to reinforce the "fintech/dev" precision of the chatbot.

Hierarchy is maintained through weight rather than just size. Headlines should feel bold and grounded. For mobile devices, large display type should scale down by roughly 15% to maintain readability without excessive wrapping.

## Layout & Spacing

The layout follows a **Fluid Grid** model based on an 8px base unit. 

- **Desktop:** 12-column grid with a 1280px max-width. Gutters are fixed at 24px to provide ample breathing room for glassmorphic effects to shine.
- **Mobile:** 4-column grid with 16px side margins. 

Spacing between components should be generous. Chat bubbles and data cards should use a 16px internal padding (2 units) to ensure content does not feel cramped against the rounded corners. Grouped elements (like a label and its input) should use 8px spacing, while distinct sections should use 48px or more to maintain a "premium" airy feel.

## Elevation & Depth

Depth is conveyed through **Glassmorphism** and **Luminous Outlines** rather than traditional drop shadows.

- **Level 1 (Base):** Deep Midnight Blue (#0B0F19).
- **Level 2 (Containers/Cards):** Charcoal (#121826) with 80% opacity and a 20px backdrop blur. Borders are 1px solid, using a low-opacity white (10%) or a subtle gradient of the primary colors.
- **Level 3 (Popovers/Modals):** Increased transparency (60% opacity) with a heavier backdrop blur (40px) and a "Glow State" border (Cyan or Purple at 30% opacity).

Avoid black shadows. Use colored "outer glows" (spread 10px, blur 20px) using the Cyan or Purple accent colors at very low opacity (15%) to make active elements appear as if they are emitting light.

## Shapes

The shape language is dominated by **Pill-shaped (3)** geometry. This softness contrasts with the technical dark theme to make the chatbot feel approachable and "organic" despite its high-tech nature.

- **Buttons & Inputs:** Always fully rounded (pill-shaped).
- **Cards & Sidebars:** Use `rounded-xl` (1.5rem / 24px) to maintain a consistent radius that complements the pill-shaped internal elements.
- **Icons:** Should feature rounded terminals and consistent line weights (2px) to match the typography.

## Components

### Buttons
Primary buttons are pill-shaped with a vibrant Cyan-to-Purple gradient. They feature a subtle outer glow of the same color on hover. Text is bold and high-contrast (dark blue on light backgrounds).

### Chat Bubbles
User messages are outlined in Cyan with a 10% Cyan fill. The Chatbot's responses use the glassmorphic style: a Charcoal base, 20px blur, and a 1px Purple border to signify AI-processing.

### Input Fields
Elevated glass surfaces with a 1px border. When focused, the border transitions to a 2px Cyan-to-Purple gradient glow, and the background blur intensity increases.

### Cards
Used for financial data summaries. They should feature "Glassmorphic" properties: backdrop-filter: blur(20px) and a semi-transparent background. Headers within cards should use the **JetBrains Mono** label style for a technical aesthetic.

### Progress Indicators / Charts
Line charts should use glowing neon paths (Cyan) with a soft gradient area fill underneath. Data points should emit a small glow on hover.

### Sidebars
Fixed-position glass panels (left-aligned) with a vertical 1px border on the right. Icons within the sidebar utilize the Electric Gold accent when in an "Active" state to highlight premium navigation areas.