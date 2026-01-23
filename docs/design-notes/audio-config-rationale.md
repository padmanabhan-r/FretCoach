# Audio Config Design: Scale Persistence

## Current State

The `audio_config.json` file currently contains both:
1. **Audio hardware settings** (input_device, output_device, channels)
2. **Practice session settings** (scale_name, scale_type, strictness, sensitivity, ambient_lighting)

Example:
```json
{
  "input_device": 1,
  "output_device": 1,
  "guitar_channel": 1,
  "channels": 2,
  "scale_name": "A Minor",
  "scale_type": "pentatonic",
  "ambient_lighting": true,
  "strictness": 0.5,
  "sensitivity": 0.5
}
```

## Why Are Scales in Audio Config?

Scales are NOT truly "hardcoded"—they are **persisted as the last-used value**. Here's the flow:

1. **Audio Setup Phase** → User configures audio devices → Saved to `audio_config.json`
2. **Mode Selection Phase** → User chooses Manual or AI mode
3. **Scale Selection Phase**:
   - **Manual Mode**: User selects a scale → Merged into config and saved to `audio_config.json`
   - **AI Mode**: AI recommends a scale → Merged into config and saved to `audio_config.json`
4. **Session Start** → Reads config from memory (which includes the scale)
5. **Next Launch** → Loads last-used config including scale

## The Design Issue

This architecture conflates two separate concerns:

| Concern | Scope | Should Persist? |
|---------|-------|----------------|
| **Audio Hardware Config** | Device-level (which audio interface to use) | Yes - across sessions |
| **Practice Session Config** | Session-level (what to practice, how strict) | No - chosen per session |

**Problem**: Scales are session-specific but are persisted in a device-level configuration file.

## Why This Works (For Now)

The current design works because:
- Each session re-selects the scale (Manual mode) or gets a fresh AI recommendation (AI mode)
- The persisted scale is only used as a **default** if the app is relaunched
- Users don't typically switch scales mid-session

## Proposed Refactoring (Future)

Separate configuration into two files:

### 1. `audio_hardware_config.json` (Device-level)
```json
{
  "input_device": 1,
  "output_device": 1,
  "guitar_channel": 1,
  "channels": 2
}
```
**Persistence**: Always saved, loaded on app start

### 2. `session_defaults.json` (Session-level)
```json
{
  "scale_name": "A Minor",
  "scale_type": "pentatonic",
  "ambient_lighting": true,
  "strictness": 0.5,
  "sensitivity": 0.5
}
```
**Persistence**: Optional defaults, overridden per session

## Rationale for Current Design

The unified config approach was chosen for simplicity:
- Single file to manage
- Single API endpoint (`/config`)
- Scale is always available when session starts
- No need for separate default management

**Trade-off**: Mixing device-level and session-level concerns.

## Recommendation

For the current milestone, **keep the unified approach**. The system works correctly because:
1. Scales are selected/recommended before each session
2. The persisted value acts as a sensible default
3. No functional issues arise from this design

**Future consideration**: If FretCoach adds multi-device support or session templates, separate the configs at that time.

---

**Status**: Design documented, no immediate action required. Current behavior is intentional and functional.
