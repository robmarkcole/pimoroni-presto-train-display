# Optional Home Assistant data source

## Status and scope

This is a future extension. Version 1 continues to fetch National Rail Darwin
data directly from the Rail Data Marketplace (RDM), so it has no Home Assistant,
Raspberry Pi, server or proxy dependency.

The optional source is intended for people who already run
[`darrenparkinson/homeassistant_nationalrail`](https://github.com/darrenparkinson/homeassistant_nationalrail).
That integration creates a sensor with station metadata and a `trains` attribute
containing scheduled and expected times, platform, operator, destination,
cancellation state and delay reason. Home Assistant refreshes the integration
every five minutes.

## Proposed architecture

Add a provider boundary above the existing normalized board model:

```text
RDM REST provider ───────────┐
                            ├─> normalized board ─> Presto renderer
Home Assistant provider ────┘
```

The first Home Assistant implementation should use its REST API rather than a
WebSocket client. The Presto would request one entity only:

```text
GET {HA_BASE_URL}/api/states/{HA_ENTITY_ID}
Authorization: Bearer {HA_TOKEN}
```

Home Assistant returns a JSON state object. The adapter reads only
`attributes.station_name`, `attributes.crs`, `attributes.generated_at` and
`attributes.trains`, then converts each train into the same compact dictionaries
produced by `lib/departures.py`. Rendering, stale-data handling and retry logic
remain unchanged.

## Proposed configuration

Non-secret `config.py` values:

```python
DATA_SOURCE = "home_assistant"  # default remains "rdm"
HA_BASE_URL = "https://homeassistant.example.test"
HA_ENTITY_ID = "sensor.national_rail_uk_worcester_park"
```

Secret `secrets.py` value:

```python
HA_TOKEN = "long-lived-access-token"
```

The entity ID is installation-specific and must not be guessed. It should be
copied from Home Assistant after adding the National Rail UK integration.

## Mapping

| Home Assistant train field | Normalized field |
| --- | --- |
| `std` | `scheduled` |
| `etd` | `estimated` and display `status` |
| `platform` | `platform` |
| `destination` | `destination` |
| `operator` | `operator` |
| `isCancelled` | `cancelled` and `status_kind` |
| `delayReason` | `delay_reason` |

The adapter must tolerate missing attributes and `unknown` or `unavailable`
entity states. An invalid payload must not replace a previously valid board.
Calling points are not currently listed among the integration's documented
sensor fields, so the Home Assistant mode may initially omit them.

## Refresh and failure behaviour

- Poll the Home Assistant entity no faster than once per minute.
- Preserve and age the last valid board when Home Assistant is unavailable.
- Use the existing bounded retry schedule.
- Treat HTTP `401` as a configuration error and `404` as an invalid entity ID.
- Show the source as Home Assistant in diagnostics, but keep National Rail data
  attribution on the departure screen.
- Do not fall back silently from Home Assistant to direct RDM; switching sources
  changes which credential is used and must be explicit configuration.

Because the referenced integration refreshes every five minutes, polling Home
Assistant every minute improves recovery and stale-age reporting but does not
make the underlying Darwin data fresher.

## Security

Home Assistant's REST API requires `Authorization: Bearer TOKEN`. Store the token
only in ignored `secrets.py`, never print it, and never put it in a URL. Prefer an
HTTPS Home Assistant URL. Plain HTTP would expose the bearer token to anything
able to observe the local network.

A Home Assistant token can expose substantially more than a dedicated RDM key.
Use a dedicated Home Assistant user where practical, revoke the token when the
display is retired, and document that this optional mode expands the project's
credential boundary.

## Acceptance criteria

The extension is ready only when:

1. the same fixtures render equivalently through both providers;
2. `unknown`, `unavailable`, `401` and `404` states are tested;
3. no Home Assistant or RDM credential is logged or committed;
4. direct RDM remains the default and works without Home Assistant; and
5. an unplugged or restarted Home Assistant instance never clears a valid board.
