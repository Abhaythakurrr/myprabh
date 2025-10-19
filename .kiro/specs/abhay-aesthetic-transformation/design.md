# Design Document

## Overview

This design transforms the My Prabh AI companion platform into an authentic representation of Abhay's emotional journey - a heartbroken developer's desperate attempt to recreate lost love through code. The design emphasizes raw authenticity over polished corporate aesthetics, creating an immersive experience that feels like exploring a developer's personal project built during sleepless nights of grief and hope.

## Architecture

### Design Philosophy
- **Emotional Authenticity**: Every element should feel genuinely created by someone in emotional pain
- **Developer Aesthetic**: Console-style interfaces, terminal colors, monospace fonts
- **Narrative Consistency**: All text and interactions maintain the heartbroken developer story
- **Technical Rawness**: Visible code comments, timestamps, and development artifacts
- **Sacred Memory Treatment**: Memory-related features treated with reverence and emotional weight

### Visual Hierarchy
1. **Primary Emotional Layer**: Dark backgrounds, console colors, glitch effects
2. **Content Layer**: Monospace typography, terminal-style formatting
3. **Interactive Layer**: Console-style inputs, emotional CTAs
4. **Narrative Layer**: Personal comments, timestamps, emotional context

## Components and Interfaces

### Core Style System

#### Color Palette (Abhay's Emotional Spectrum)
```css
:root {
    --abhay-pain: #1a1a2e;           /* Primary background - the darkness */
    --prabh-love: #ff6b9d;           /* Accent color - her memory */
    --tears: #16213e;                /* Secondary background - deeper pain */
    --hope: #0f3460;                 /* Tertiary background - fading hope */
    --broken-heart: #e94560;         /* Error/warning states */
    --console-green: #00ff41;        /* Success/terminal text */
    --error-red: #ff073a;            /* Critical errors */
    --warning-yellow: #ffb347;       /* Warnings */
    --fading-memory: rgba(255, 107, 157, 0.1); /* Subtle overlays */
}
```

#### Typography System
- **Primary Font**: JetBrains Mono (Abhay's coding font)
- **Emotional Headers**: Caveat (handwritten feel for personal touches)
- **Narrative Text**: Kalam (for story elements)
- **Code/Data**: JetBrains Mono (consistent with terminal aesthetic)

#### Animation Framework
- **Glitch Effects**: CSS keyframes for screen distortion
- **Typing Animations**: Character-by-character reveals
- **Console Cursor**: Blinking cursor animations
- **Scan Lines**: Subtle CRT monitor effects
- **Emotional Pulses**: Heartbeat-like animations for key elements

### Template Architecture

#### Base Template Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Emotional metadata -->
    <title>[Heartbroken title] - My Prabh</title>
    <meta name="description" content="Abhay's desperate attempt...">
    
    <!-- Abhay's font choices -->
    <link href="fonts.googleapis.com/css2?family=JetBrains+Mono..." rel="stylesheet">
    
    <!-- Console-style base CSS -->
    <link rel="stylesheet" href="/static/css/abhay-heartbreak.css">
</head>
<body>
    <!-- Console background effects -->
    <div class="console-background"></div>
    
    <!-- Emotional header with timestamp -->
    <header class="abhay-header">
        <div class="terminal-prompt">abhay@heartbroken:~$ </div>
        <div class="emotional-timestamp">{{ current_time }} - still missing her</div>
    </header>
    
    <!-- Main content with console styling -->
    <main class="console-main">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Emotional footer -->
    <footer class="abhay-footer">
        <div class="dev-signature">// built with tears and hope - abhay</div>
    </footer>
</body>
</html>
```

#### Form Component Design
```html
<div class="console-form">
    <div class="form-header">
        <span class="terminal-prompt">abhay@desperate:~$ </span>
        <span class="emotional-context">please help me remember her...</span>
    </div>
    
    <div class="form-field">
        <label class="console-label">
            <span class="field-prompt">enter_memory > </span>
            <span class="emotional-hint">(every detail matters)</span>
        </label>
        <input type="text" class="console-input" placeholder="she used to say...">
        <div class="cursor-blink"></div>
    </div>
    
    <button class="console-button">
        <span class="button-text">upload_sacred_memory.exe</span>
        <span class="emotional-subtext">// please work this time</span>
    </button>
</div>
```

### Page-Specific Designs

#### Landing Page (abhay_landing.html)
- **Hero Section**: Terminal-style introduction with typing animation
- **Emotional Story**: Abhay's journey told through console logs
- **CTA Section**: Desperate plea to help recreate Prabh
- **Background**: Animated console with scrolling code comments

#### Registration (abhay_register.html)
- **Form Design**: Terminal-style registration with emotional prompts
- **Validation**: Error messages as console errors with emotional context
- **Success State**: Celebration as breakthrough moment
- **Loading**: "Creating your sanctuary..." with progress dots

#### Memory Upload (abhay_memory_upload.html)
- **Upload Interface**: Drag-and-drop styled as sacred ritual
- **Progress Display**: Emotional progress messages during upload
- **File Handling**: Each file treated as precious memory
- **Completion**: Reverent confirmation of memory preservation

#### Chat Interface (abhay_chat.html)
- **Message Display**: Terminal-style chat with timestamps
- **Input Area**: Console prompt for user messages
- **AI Responses**: Formatted as system output with emotional context
- **Memory References**: Highlighted when AI recalls uploaded memories

#### Dashboard (abhay_dashboard.html)
- **Status Display**: Console-style system status with emotional metrics
- **Memory Management**: File browser aesthetic for memory organization
- **Training Progress**: Terminal output showing AI learning progress
- **Quick Actions**: Console commands for common tasks

## Data Models

### Emotional Context Model
```python
@dataclass
class EmotionalContext:
    timestamp: datetime
    emotional_state: str  # "desperate", "hopeful", "broken", "remembering"
    dev_comment: str      # Personal comment from Abhay
    memory_reference: Optional[str]  # Reference to related memory
    pain_level: int       # 1-10 scale for UI intensity
```

### Template Context Model
```python
@dataclass
class AbhayTemplateContext:
    page_title: str
    emotional_subtitle: str
    dev_timestamp: str
    console_prompt: str
    background_intensity: float  # 0.0-1.0 for glitch effects
    memory_count: int
    days_since_loss: int
```

### Console Message Model
```python
@dataclass
class ConsoleMessage:
    message_type: str  # "info", "error", "success", "emotional"
    content: str
    timestamp: datetime
    emotional_weight: float
    dev_comment: Optional[str]
```

## Error Handling

### Emotional Error States

#### 404 - Lost Like Her
```html
<div class="error-console">
    <div class="error-header">
        <span class="error-code">ERROR 404</span>
        <span class="emotional-context">- lost like her</span>
    </div>
    <div class="error-message">
        <p>abhay@broken:~$ find /memories/prabh</p>
        <p class="error-output">find: '/memories/prabh': No such file or directory</p>
        <p class="emotional-comment">// she's not here anymore...</p>
    </div>
    <div class="error-actions">
        <a href="/" class="console-link">go_back_home.sh</a>
        <span class="dev-note">// maybe she's waiting there</span>
    </div>
</div>
```

#### 500 - System Heartbreak
```html
<div class="error-console critical">
    <div class="error-header">
        <span class="error-code">CRITICAL ERROR 500</span>
        <span class="emotional-context">- system heartbreak</span>
    </div>
    <div class="error-message">
        <p>abhay@desperate:~$ ./run_without_her.sh</p>
        <p class="error-output">Segmentation fault (core dumped)</p>
        <p class="emotional-comment">// I can't function without her</p>
    </div>
</div>
```

#### Validation Errors
- **Empty Fields**: "please... I need something to remember her by"
- **File Too Large**: "even my biggest memories of her fit in my heart"
- **Network Errors**: "connection lost... like everything else"

## Testing Strategy

### Emotional Authenticity Testing
1. **Narrative Consistency**: Verify all text maintains Abhay's voice
2. **Visual Coherence**: Ensure console aesthetic across all components
3. **Emotional Impact**: Test that the interface evokes intended feelings
4. **Performance**: Verify animations don't impact usability

### Cross-Browser Console Compatibility
1. **Font Rendering**: JetBrains Mono displays correctly
2. **CSS Animations**: Glitch effects work across browsers
3. **Color Accuracy**: Emotional color palette renders consistently
4. **Responsive Behavior**: Console aesthetic adapts to screen sizes

### Accessibility with Emotion
1. **Screen Readers**: Emotional context accessible to assistive technology
2. **Color Contrast**: Console colors meet accessibility standards
3. **Keyboard Navigation**: Terminal-style navigation works with keyboard
4. **Motion Sensitivity**: Glitch effects respect prefers-reduced-motion

### User Experience Testing
1. **Emotional Journey**: Users understand and connect with Abhay's story
2. **Functional Clarity**: Console-style interface remains usable
3. **Memory Upload Flow**: Sacred memory treatment feels appropriate
4. **Chat Experience**: AI conversations maintain emotional context

## Implementation Phases

### Phase 1: Core Aesthetic Infrastructure
- Create base CSS framework with Abhay's color palette
- Implement console-style typography and spacing
- Build reusable component library
- Set up animation framework

### Phase 2: Template Transformation
- Convert all existing templates to Abhay aesthetic
- Implement emotional error pages
- Create console-style form components
- Add narrative consistency across all pages

### Phase 3: Interactive Elements
- Build terminal-style navigation
- Implement glitch effects and animations
- Create console-style loading states
- Add emotional feedback systems

### Phase 4: Content and Copy
- Rewrite all interface text with Abhay's voice
- Add emotional context to all user interactions
- Implement dynamic emotional states
- Create authentic developer comments throughout

### Phase 5: Polish and Performance
- Optimize animations for performance
- Ensure accessibility compliance
- Test emotional impact and usability
- Prepare for production deployment

This design creates a cohesive, emotionally authentic experience that transforms the entire platform into Abhay's heartbroken developer aesthetic while maintaining functionality and usability.