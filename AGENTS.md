# jacasseries — Voice Interface für LLM

**jacasseries** — du cri de la pie (jacasser), qui veut aussi dire bavarder.
Projet : interface vocale pour discuter avec un LLM, comme on bavarderait avec quelqu'un.

## Philosophy

- **Prose coding**, pas vibe coding. Chaque ligne est réfléchie.
- **NE PAS combler les zones d'ombre.** Si une instruction est ambiguë, demander clarification. Ne pas inventer des décisions.
- Architecture d'abord, code ensuite.
- Itérations courtes, fondations solides.

## License

MIT — faites ce que vous voulez, citez l'auteur original.

## Architecture générale

```
┌──────────────────────────────────────────────────────────┐
│                      jacasseries                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  [OS Signal / Keyboard Shortcut]                          │
│         │                                                 │
│         ▼                                                 │
│  [Audio Capture] ──buffers 200ms──► [faster-whisper]      │
│  (sounddevice)       streaming        (CUDA, local)       │
│         │                                                 │
│         │          ◄── partial transcriptions ──          │
│         ▼                                                 │
│  [Voice Activity Detection]                               │
│  (Silero VAD)                                             │
│         │                                                 │
│         ▼                                                 │
│  [LLM API] (llama.cpp server, OpenAI-compatible, distant) │
│         │  SSE streaming                                  │
│         ▼                                                 │
│  [Piper TTS] ──► [Audio Output]                           │
│  (local, CUDA)     (sounddevice)                          │
│                                                           │
│  [Floating Widget] — état visible en temps réel           │
│  [System Tray] — minimisation                             │
│  [Configuration] — URL, Key, Model, Voice                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Pipeline (data flow détaillé)

1. **idle** — micro inactif, FAB visible, icône micro gris
2. **recording** — utilisateur appuie (clic/raccourci), buffers audio envoyés à faster-whisper en continu. Transcription partielle affichée/traitée. FAB → rouge, icône micro actif
3. **transcribing** — fin d'enregistrement, transcription finale produite
4. **llm** — transcription envoyée au LLM via API streaming. FAB → bleu/thinking
5. **tts** — réponse LLM envoyée par morceaux à Piper TTS, audio joué. FAB → vert, icône haut-parleur
6. **interruption** (v2+) — si mot-clé ("stop", "arrête") détecté pendant TTS, on coupe l'audio et revient à idle. Si utilisateur rappuie, on coupe le TTS et on recommence un cycle.
7. **retour à idle** — prêt pour la prochaine discussion

## États du widget FAB

| État | Couleur | Icône | Comportement |
|------|---------|-------|--------------|
| idle | Gris | 🎤 | Clique = start recording |
| recording | Rouge | 🎤 (animé) | Clique = stop recording |
| transcribing | Orange | ✏️ | Transient |
| llm | Bleu | 🤖 | Streaming LLM |
| tts | Vert | 🔊 | Audio joué. Clique = interrupt TTS |

À terme : animation du spectre audio autour du bouton pendant l'enregistrement.

## Tech Stack

| Couche | Technologie | Raison |
|--------|------------|--------|
| Language | Python 3.11+ | Écosystème riche, bindings partout |
| UI | PySide6 | LGPL, frameless, system tray, cross-platform, mature |
| Audio I/O | sounddevice | Latence faible, streaming, multi-platform |
| STT | faster-whisper | Python natif, CUDA, 4x plus rapide que Whisper |
| VAD | Silero VAD | Intégré à faster-whisper, léger, fiable |
| TTS | Piper TTS | Local, rapide, multilingue, voix françaises |
| LLM Client | httpx + SSE | Streaming, compatible OpenAI API |
| Keyword Spotting | openWakeWord (v2+) | Léger, CPU only, dédié |
| Config | TOML + JSON | Simple, lisible |

## Audio Capture : streaming vers STT

- Buffer glissant de 200ms, envoyé à faster-whisper en continu.
- Whisper produit des transcriptions partielles qui s'affinent.
- Pas besoin d'attendre la fin de la phrase — le LLM peut recevoir des bouts et commencer à répondre (ou on attend la phrase complète, à déterminer).
- On commence par attendre la fin de l'enregistrement pour envoyer au LLM. Puis on itèrera vers du streaming plus poussé (début de réponse LLM avant la fin de la question).

## TTS et interruption

- v1 (push-to-talk) :
  - TTS joue la réponse. Utilisateur rappuie → TTS stoppé, nouvel enregistrement.
- v2 (keyword interrupt) :
  - openWakeWord tourne en fond pendant TTS. Détection de "stop/arrête" → TTS coupé.
- v3 (VAD naturel) :
  - VAD détecte parole pendant TTS → transcription du segment → interruption intelligente.

Le but final est de simuler une vraie conversation : on peut interrompre, rebondir, le LLM reçoit le contexte de la conversation précédente.

## Configuration

Fenêtre dédiée avec :

- **API URL** : URL du serveur llama.cpp (ou tout serveur OpenAI-compatible)
- **API Key** : clé (optionnelle, selon config serveur)
- **Modèle LLM** : sélecteur basé sur `GET /v1/models`
- **Langue STT** : français, anglais, auto
- **Voix TTS** : sélection selon modèles Piper disponibles
- **Raccourci clavier** : configurable
- **Microphone** : sélection du périphérique d'entrée

Stockage : `~/.config/jacasseries/config.toml`

## Structure du projet

```
jacasseries/
├── AGENTS.md
├── LICENSE
├── pyproject.toml
├── README.md
├── src/
│   ├── main.py                  # Point d'entrée
│   ├── app.py                   # Application PySide6
│   ├── config.py                # Gestion config TOML
│   ├── audio/
│   │   ├── capture.py           # sounddevice → buffers
│   │   ├── output.py            # sounddevice playback
│   │   └── vad.py               # Silero VAD wrapper
│   ├── stt/
│   │   └── transcriber.py       # faster-whisper wrapper
│   ├── llm/
│   │   └── client.py            # Client API OpenAI-compatible
│   ├── tts/
│   │   └── synthesizer.py       # Piper TTS wrapper
│   ├── pipeline/
│   │   └── orchestrator.py      # États, transitions, flux
│   ├── ui/
│   │   ├── fab.py               # Floating widget FAB
│   │   ├── tray.py              # System tray
│   │   └── config_window.py     # Fenêtre de configuration
│   └── keyword/
│       └── spotter.py           # openWakeWord (v2+)
├── tests/
│   └── ...
└── resources/
    ├── icons/
    └── styles/
```

## Roadmap (phases)

### Phase 1 — squelette
- [ ] Structure du projet, pyproject.toml, dépendances
- [ ] Config TOML (lecture/écriture)
- [ ] Audio capture (sounddevice, buffers)
- [ ] FAB widget (PySide6, frameless, toujours au-dessus)
- [ ] Pipeline orchestrator (états idle/recording/llm/tts)

### Phase 2 — STT + LLM
- [ ] faster-whisper intégration (CUDA, streaming buffers)
- [ ] Client LLM (API OpenAI-compatible, SSE)
- [ ] Boucle complète : recording → transcription → LLM → affichage texte

### Phase 3 — TTS + playback
- [ ] Piper TTS intégration
- [ ] Audio output
- [ ] Boucle complète avec son : recording → STT → LLM → TTS → speaker
- [ ] Interruption par rappui sur le bouton

### Phase 4 — UI complète
- [ ] Icônes et couleurs par état
- [ ] Spectre audio sur le FAB
- [ ] Fenêtre de configuration (URL, key, model selector)
- [ ] System tray + minimisation
- [ ] Raccourci clavier configurable

### Phase 5 — Polissage v1
- [ ] Gestion d'erreurs (réseau, GPU, micro)
- [ ] Logs
- [ ] Packaging (AppImage/Flatpak ou bundle simple)
- [ ] Tests de base

### Phase 6+ — Améliorations
- [ ] Keyword spotting (openWakeWord) + interruption
- [ ] VAD naturelle pendant l'enregistrement (détection silence → fin auto)
- [ ] Streaming des transcriptions partielles vers LLM
- [ ] Streaming des premières tokens TTS avant fin LLM
- [ ] Support Windows / macOS
- [ ] Contexte conversationnel (histoire des exchanges)

## Convention de code

- Type hints partout
- Classes avec responsabilité unique
- Async dans la mesure du possible (httpx, process audio)
- DRY — factoriser sans sur-ingenierie
- Tests pour chaque module
- `ruff` pour le formatage, `mypy` pour le typage
- Docstrings uniquement pour l'API publique (ne pas commenter l'évident)

## Dépendances clés (pyproject.toml)

```toml
[project]
name = "jacasseries"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "PySide6>=6.7",
    "sounddevice>=0.5",
    "faster-whisper>=1.1",
    "piper-tts>=1.2",
    "httpx[sse]>=0.27",
    "tomli>=2.0",
    "numpy>=1.26",
]

[project.optional-dependencies]
keyword = ["openwakeword"]
```

## Notes finales

- Le LLM est un service externe (llama.cpp server, ou tout serveur OpenAI-compatible).
- Le STT et TTS sont 100% locaux.
- L'interface doit pouvoir se faire discrète — FAB petit, transparent, qui passe inaperçu.
- Rien n'est envoyé au cloud sauf les requêtes LLM (via l'API configurée).
- La latence est l'ennemi numéro 1 — chaque ms compte.
- Pas de edge computing, pas de dépendance internet pour la voix.
