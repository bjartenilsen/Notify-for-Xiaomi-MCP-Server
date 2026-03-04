# Spec: Notify for Xiaomi MCP Server

## Oversikt
Bygg en lokal MCP-server i Python som laster ned `backup.db` fra Google Drive
og eksponerer helsedata fra Notify for Xiaomi som MCP-verktøy tilgjengelig i Claude Desktop.

---

## Kontekst
- Backup-filen heter `backup.db` og ligger i Google Drive-mappen `Notify for xiaomi`
- Filen er en SQLite-database (~163 MB) eksportert fra Notify for Xiaomi-appen
- Serveren skal kjøre lokalt på Windows via stdio-transport
- Autentisering mot Google Drive via OAuth2 med `credentials.json`

---

## Krav

### Funksjonelle krav

1. **Google Drive-integrasjon**
   - Autentiser mot Google Drive med OAuth2 (`credentials.json` + `token.pickle`)
   - Finn mappen `Notify for xiaomi` i Drive
   - Last ned `backup.db` til en lokal temp-mappe
   - Lagre token slik at bruker ikke må logge inn hver gang

2. **MCP-verktøy som skal implementeres**

   | Verktøynavn | Beskrivelse |
   |---|---|
   | `nxk_sync_database` | Last ned / oppdater backup.db fra Google Drive |
   | `nxk_list_tables` | List alle tabeller med kolonner og radtall |
   | `nxk_get_sleep` | Hent søvndata med lesbare tidsstempler |
   | `nxk_get_heart_rate` | Hent pulsdata (BPM) med tidsstempler |
   | `nxk_get_activity` | Hent aktivitetsdata (skritt, kalorier, distanse) |
   | `nxk_query` | Kjør vilkårlig SELECT-spørring (kun SELECT tillatt) |

3. **Databehandling**
   - Konverter Unix-tidsstempler (ms og s) til lesbare datostrenger (YYYY-MM-DD HH:MM)
   - Støtte filtrering på dato-range (start_date / end_date) der relevant
   - Støtte paginering via `limit`-parameter (default 100, maks 1000)
   - Returner data som JSON

### Ikke-funksjonelle krav
- Kun lesoperasjoner mot databasen (ingen INSERT/UPDATE/DELETE)
- Tydelige feilmeldinger på norsk hvis fil mangler eller Drive-tilgang feiler
- Transport: `stdio` (for Claude Desktop på Windows)

---

## Teknisk stack

- **Språk**: Python 3.11+
- **MCP-rammeverk**: `mcp[cli]` med FastMCP
- **Google Drive**: `google-api-python-client`, `google-auth-oauthlib`
- **Database**: `sqlite3` (innebygd i Python)
- **Input-validering**: Pydantic v2

---

## Filstruktur

```
notify_xiaomi_mcp/
├── server.py           # Hovedfil – MCP-serveren
├── requirements.txt    # Python-avhengigheter
├── credentials.json    # (brukeren legger inn selv fra Google Console)
└── token.pickle        # (genereres automatisk ved første innlogging)
```

---

## Claude Desktop-konfigurasjon

Serveren skal kunne legges til i `%APPDATA%\Claude\claude_desktop_config.json` slik:

```json
{
  "mcpServers": {
    "notify_xiaomi": {
      "command": "python",
      "args": ["C:\\FULL\\STI\\TIL\\notify_xiaomi_mcp\\server.py"]
    }
  }
}
```

---

## Akseptansekriterier

- [ ] `nxk_sync_database` laster ned `backup.db` fra riktig Drive-mappe
- [ ] `nxk_list_tables` viser alle tabeller med kolonnenavn og antall rader
- [ ] `nxk_get_sleep` returnerer søvndata med lesbare datoer
- [ ] `nxk_get_heart_rate` returnerer pulsmålinger med lesbare datoer
- [ ] `nxk_get_activity` returnerer aktivitetsdata med lesbare datoer
- [ ] `nxk_query` avviser alle ikke-SELECT-spørringer med feilmelding
- [ ] Serveren starter uten feil i Claude Desktop
- [ ] Token lagres lokalt slik at re-autentisering ikke kreves ved hver oppstart
