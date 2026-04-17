# AI Agent Skills & Context

This file provides context for AI agents working on the **TTS Chat** codebase. It helps ensure consistency, avoid redundancy, and maintain the established tech stack.

## 🛠 Tech Stack & Environment

### Backend
- **Python Version**: `3.10+` (specifically tested on 3.10 - 3.13).
- **Virtual Environment**: `.venv` (standard location in root).
- **Framework**: Flask (`flask==3.1.3`).
- **Core Dependencies**:
  - `kokoro`: Text-to-Speech synthesis.
  - `torch` / `numpy`: ML backends for TTS.
  - `openai`: LLM client for interacting with LM Studio (local server).
  - `flask-cors`: Cross-Origin Resource Sharing.
  - `Flask-Squeeze`: Content compression for responses.
  - `sounddevice`: Audio playback utilities.

### Frontend
- **Architecture**: Single Page Application (SPA) in `web/`.
- **Technologies**: Vanilla JavaScript (ES6+), CSS3 (Modern/Vanilla), HTML5.
- **Styling**:
  - Custom design system using CSS variables (`:root`).
  - **Aesthetics**: Modern dark mode (`#0b141a`), glassmorphism, smooth transitions.
  - Responsive layout with a sidebar and main chat panel.
- **Icons**: SVG-based, defined as constants in `app.js`.

---

## 🏗 Project Architecture & Key Functions

### Backend (`app/`)
- `run.py`: Entry point for the Flask server.
- `app/routes/api.py`: REST endpoints (`/api/chat`, `/api/tts`, `/api/models`, `/api/voices`).
- `app/services/`: Core logic (LLM integration, TTS synthesis).
- `app/utils/`:
  - `audio.py` -> `audio_to_wav_base64(audio, sample_rate)`: Converts raw audio to base64 WAV.
  - `text.py` -> `strip_markdown(text)`: Cleans markdown for legal TTS reading.

### Frontend (`web/`)
- `web/app.js`: Main state management and DOM interaction.
  - **State**: Central `state` object.
  - **DOM**: Central `elements` object for caching selectors.
  - **Persistence**: `saveState()` and `loadState()` use `localStorage` (`lm_tts_chats_v1`).
  - **Utilities**:
    - `newId()`: Generates unique message/chat IDs.
    - `parseMarkdown(text)`: Renders markdown to HTML (using marked-like logic).
    - `requestAssistantResponse(chat)`: Orchestrates API calls and UI updates.
  - **UI Patterns**:
    - `renderMessages()`: Diff-less full re-render of message list.
    - `updateChatHeader()`: Updates the header info based on active chat.

---

## 💡 Developer Guidelines (For AI Agents)

1. **Don't Re-invent**:
   - **Backend**: Use `strip_markdown` before sending text to TTS. Use `audio_to_wav_base64` for any audio output.
   - **Frontend**: Use `newId()` for new entities. Always call `saveState()` and `render()` (or specialized renderers like `renderMessages`) after state changes.
2. **Design First**:
   - Maintain the premium, dark-mode design. Use existing CSS variables from `styles.css`.
   - Use `showModal()` for `<dialog>` elements.
   - For random colors, use `generateRandomSoftColor()` (HSL-based).
3. **No Placeholders**:
   - When adding new features, provide a working implementation (e.g., using `generate_image` for assets).
4. **Dependency Management**:
   - Avoid adding new Python packages.
   - Strictly NO frontend frameworks (React, Vue, etc.).
