# KrishiVeda — UI Animation & Best Skills Guide

> Figma-inspired (AgroShare) + designer-skills pack — implemented in `frontend/tailwind.config.js:109`, `frontend/src/index.css:18`, `frontend/src/components/**`, `frontend/src/pages/Pages.jsx`

## Best Skills for UI (from 273-skill pack)

### 1) Core System (design-systems)
| Skill | Why for KrishiVeda |
|-------|-------------------|
| **motion-system** | Defines product-wide duration/easing tokens + `prefers-reduced-motion` handling. We ship `instant 50ms, fast 120ms, base 200ms, moderate 300ms, slow 400ms, deliberate 600ms` + `standard/decelerate/accelerate/spring` easing. |
| **design-token** | Single source for farm palette, stone neutrals, typography, spacing, shadows — ensures Figma mint `#f1f8ef` + farm `#2E8B57/#28784c` stays consistent. |
| **component-spec** | Card/button/chip/badge specs with states (default/hover/press/disabled) → `ui.jsx:46` |
| **accessibility-audit** | AA contrast (4.5:1 text, 3:1 UI), 44px touch targets, focus-ring, keyboard nav |

### 2) Visual (ui-design)
| Skill | Applied |
|-------|---------|
| **color-system** | Full tonal scales farm/success/warn/danger/info/stone, semantic mapping |
| **typography-scale** | 12-48px display/h1/h2/h3/subheading/body/caption, Noto Sans 11-lang stack |
| **spacing-system** | 4px base, 2xs-3xl scale, law-of-proximity for card gaps |
| **layout-grid** | 4-col mobile / 12-col desktop, landscape `max-w-5xl` sidebar + content |
| **visual-hierarchy** | Hero (plantation + weather) > quick actions > alerts > voice CTA |
| **aesthetic-usability** | Rounded-3xl white cards, soft shadows, mint background → perceived trust |
| **data-visualization** | Dark-green weather widget, soil health circular progress, forecast chips |

### 3) Interaction (interaction-design)
| Skill | Applied |
|-------|---------|
| **animation-principles** | Easing per motion: `decelerate` on enter (cards fadeUp), `accelerate` on exit, `standard` on move |
| **micro-interaction-spec** | Trigger→Rules→Feedback→Loop for voice button (tap→listen→pulseRing→speak), button press `scale 0.97`, card `hover-lift -translate-y-0.5` |
| **interfaces-that-feel** | Soft landing (ease-out), 150-300ms for response, loading as mood (shimmer/skeleton), success toast warm `pop` |
| **form-design** | Input focus `border-farm-500 ring 2`, chip active `bg-farm-600`, error `danger-50` |

### 4) Critique & Validation (visual-critique / prototyping-testing)
- `critique-visual-hierarchy`, `critique-color`, `critique-typography` for screenshot QA
- `heuristic-evaluation` (lighthouse a11y 0.89) + `test-plan`

---

## Animation System Shipped

### Tokens (`tailwind.config.js:109`)
```js
duration: instant 50, fast 120, base 200, moderate 300, slow 400, deliberate 600
easing: standard (0.2,0,0,1), decelerate (0,0,0.2,1), accelerate (0.3,0,1,0.3), spring (0.34,1.56,0.64,1)
```

### Keyframes
- `fadeUp/slideUp/slideDown/pop` — page & card entrance (decelerate, 250-300ms)
- `float` — weather icon gentle 3s ease-in-out
- `barGrow` — harvest progress `scaleX` 600ms
- `messageSlide` — chat bubble 250ms decelerate
- `pulseRing` — voice listening halo 1.5s
- `shimmer` — skeleton loading linear 1.4s
- `shake` — error feedback

### Choreography (motion-system rules)
- Stagger `30-50ms` (we use `45ms`) for quick-action cards, `30ms` for scheme cards — total sequence <500ms
- Lead with most important (plantation → weather → quick actions)
- `will-change: transform` + `transform/opacity` only (no layout thrash)
- Reduced-motion: `@media (prefers-reduced-motion: reduce)` disables translate/scale, keeps opacity fades

### Micro-interactions Implemented
| Element | Trigger | Feedback |
|---------|---------|----------|
| Header | page load | `animate-slideDown` 300ms decelerate |
| Sidebar nav | hover/active | `translate-x-0.5` / `scale 1.02` + `bg-farm-600` |
| Quick-action cards | mount / hover | `cardEntrance` stagger 45ms + `hover:-translate-y-0.5` + `shadow-card → shadow-md` |
| Plantation progress | mount | `barGrow` origin-left 600ms delay 0.2s |
| Weather icon | always | `float` 3s infinite |
| Chat message | new message | `messageSlide` + avatar `pop` stagger 60ms |
| Scheme cards | mount | `cardEntrance` stagger 30ms |
| Voice button | listening | `pulseRing` halo + `pulseSoft` bg, press `scale 0.97` |
| Buttons | press | `pressable` `active:scale-0.97` 120ms |
| Skeletons | loading | `shimmer` linear |

### How to Verify
- Build `vite 97 modules 281.58 kB` OK
- `cards.slice(0,4).animationDelay` → `0ms|cardEntrance;45ms|cardEntrance;90ms|cardEntrance;135ms|cardEntrance`
- `prefers-reduced-motion: reduce` tested — hover-lift disabled, opacity fades preserved

### Variants Kept
- Portrait `max-w-app` bottom nav + landscape `max-w-5xl` sidebar — both respect motion tokens and reduced-motion.
