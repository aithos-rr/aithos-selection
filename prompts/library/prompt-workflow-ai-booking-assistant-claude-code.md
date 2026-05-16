---
id: prompt-workflow-ai-booking-assistant-claude-code
name: Prompt Workflow per creare un AI Booking Assistant con Claude Code
type: prompt
status: stable
version: 1.0.0
description: Sequenza cronologica di prompt per costruire passo-passo un AI Booking Assistant in Next.js 15 con Claude Code, Supabase, Vercel e n8n (live build del Yellow Tech Meeting Room Booking). Copia-incolla e personalizza per qualunque scenario di prenotazioni.
tags: [workflow, claude-code, italian, booking, supabase]
language: it
created: 2026-05-16
updated: 2026-05-16
author: riccardo
---
# Prompt Workflow per creare un AI Booking Assistant su Claude Code

Filippo Greco · Yellow Tech

Tool costruito in live: Meeting Room Booking AI per Yellow Tech
Stack: Claude Code · Supabase · Vercel · n8n · OpenRouter (per la parte AI del tool)

App live (URL pubblico): https://meeting-room-booking-six-taupe.vercel.app
Codice completo (GitHub): https://github.com/filippogreco-maker/meeting-room-booking-w4

Sotto trovi tutti i prompt usati durante la build live, in ordine cronologico. Copia, incolla e personalizza per il tuo scenario.

———

1\) CLAUDE.md iniziale (1 min)

Iniziamo un progetto Next.js 15 per gestire le prenotazioni delle sale riunioni di Yellow Tech.

Crea un file CLAUDE.md alla radice del progetto che descriva:
\- Il contesto: Yellow Tech ha 3 sale a Milano (Cliente, Brainstorming, Riunione Grande). Voglio un tool web dove i dipendenti vedono il calendario settimanale e prenotano slot vuoti.
\- Lo stack: Next.js 15 App Router, TypeScript, Tailwind CSS, Supabase per database e auth, OpenRouter per le risposte AI, Vercel per il deploy.
\- Le convenzioni: TypeScript strict mode, niente "any", componenti server di default, client solo dove serve interattività.
\- I comandi: npm run dev (server locale), npm run build (build produzione), vercel \--prod (deploy).
\- Il brand Yellow Tech: palette giallo \#FDE438 \+ blu \#444D9F \+ dark \#0F0F12, font Inter, tono visivo "tech premium".

Poi entra in Plan Mode e proponi la struttura cartelle prima di scrivere codice.

———

2\) Schema database Supabase (3 min)

Crea il file supabase/schema.sql con due tabelle:

rooms:
\- id uuid primary key default uuid\_generate\_v4()
\- name text unique (3 sale: "Sala Cliente", "Sala Brainstorming", "Sala Riunione Grande")
\- capacity int (8, 4, 15\)
\- equipment text array (es. \['TV 65"', 'whiteboard', 'webcam'\])
\- color hex string per la UI
\- image\_url text per la foto della sala
\- created\_at timestamptz default now()

bookings:
\- id uuid primary key
\- room\_id uuid foreign key \-\> rooms
\- user\_id uuid foreign key \-\> auth.users (nullable per prenotazioni anonime)
\- user\_email, user\_name text
\- start\_time, end\_time timestamptz
\- attendees\_count int
\- purpose text
\- equipment\_needed text array
\- created\_at timestamptz default now()
\- constraint: end\_time \> start\_time

Abilita RLS su entrambe. Policy:
\- rooms: select aperta a tutti
\- bookings: select aperta a tutti, insert aperta a tutti (per la demo), update/delete solo proprietario via auth.uid()

Seed le 3 sale con foto stock e colori del brand Yellow Tech.

———

3\) Pagina home con grid sale \+ modal di prenotazione (6 min)

Costruisci la home /app/page.tsx con questa struttura:

Header sticky con logo Yellow Tech a sinistra, badge "AI conflict detection" e button "Accedi" a destra.

Hero section con titolo grande ("Prenota la tua sala riunioni in 30 secondi"), sottotitolo, e una 3D shape decorativa del brand a destra.

Sezione "Disponibilità di questa settimana" con un componente RoomGrid che:
\- Carica le 3 sale via fetch GET /api/rooms
\- Carica le prenotazioni della settimana corrente via GET /api/bookings?from=...\&to=...
\- Mostra 3 card (una per sala) con foto \+ nome \+ capacità badge \+ equipment chip
\- Sotto ogni card, 5 row orizzontali (lun-ven) con timeline 9-19 sull'asse X
\- Le prenotazioni esistenti appaiono come pill colorate posizionate absolute (left% \+ width%)
\- Click su zona vuota apre BookingFormModal con orario precompilato

BookingFormModal con campi: scopo riunione, partecipanti (numero), durata (30/60/90/120 min), equipment richiesto (pill toggle), nome, email. Bottone "Controlla con AI" prima del "Conferma prenotazione".

Footer con stack visibile.

Usa Tailwind con variabili HSL nel globals.css. Niente librerie UI esterne, solo Tailwind \+ componenti custom.

———

4\) Conflict detection AI con Claude Haiku via OpenRouter (5 min)

Crea l'endpoint POST /api/bookings/check.

Riceve: room\_id, start\_time, end\_time, attendees\_count, purpose, equipment\_needed.

Step 1 \- Check deterministico:
\- Capacity: se attendees \> room.capacity → warning "high" \+ suggerisci sala più piccola tra quelle che reggono il numero
\- Overlap: query Supabase per bookings sovrapposti nella stessa sala → warning "high"
\- Equipment: confronta equipment\_needed vs room.equipment → warning "medium" per quello mancante

Step 2 \- Chiamata AI:
\- Usa fetch a https://openrouter.ai/api/v1/chat/completions
\- Header: Authorization Bearer ${OPENROUTER\_API\_KEY}, HTTP-Referer, X-Title
\- Body: model "anthropic/claude-haiku-4.5", max\_tokens 300, prompt con tutto il contesto (sala scelta, sale alternative, prenotazioni del giorno, scopo)
\- Chiedi 1-3 suggerimenti in italiano, ognuno con emoji \+ max 100 caratteri
\- Parse JSON array dalla risposta

Output schema:
{ ok: boolean, warnings: \[{type, severity, message}\], suggestions: string\[\] }

Gestisci errori AI senza bloccare i warning deterministici.

———

5\) Deploy su Vercel (3 min)

Configura il deploy con Vercel CLI:

vercel link \--yes (collega il progetto al tuo team Vercel)
vercel env add NEXT\_PUBLIC\_SUPABASE\_URL production (incolla URL)
vercel env add NEXT\_PUBLIC\_SUPABASE\_ANON\_KEY production (incolla anon key)
vercel env add SUPABASE\_SERVICE\_ROLE\_KEY production
vercel env add OPENROUTER\_API\_KEY production
vercel deploy \--prod (deploy production, restituisce l'URL pubblico)

Verifica che le env vars siano in Production scope con: vercel env ls production.

Test l'URL pubblico con: curl https://\<tuo-url\>.vercel.app/api/rooms (deve restituire 3 sale).

———

6\) Workflow n8n morning Slack reminder (4 min)

Crea un workflow n8n con 5 nodi:

Schedule Trigger (cron):
\- Espressione "0 30 8 \* \* 1-5" (ogni giorno feriale alle 8:30)
\- Timezone Europe/Rome

Code node "Build today range":
\- Calcola dayStart e dayEnd in TZ Italia per oggi
\- Output: { dayStart, dayEnd, today }

HTTP Request:
\- GET {APP\_URL}/api/bookings?from={dayStart}\&to={dayEnd}
\- APP\_URL come variabile n8n o env

Code node "Format Slack message":
\- Se 0 prenotazioni: output skip true (niente messaggio)
\- Altrimenti: raggruppa per sala, formatta in markdown Slack ("\*Sala Cliente\* (2)\\n  • 10:00-11:00 ...")

IF node: se skip true → end, se false → continua

HTTP Request "Post to Slack":
\- POST {SLACK\_WEBHOOK\_URL}
\- Body: { text: "\<messaggio formattato\>" }

Salva. Attiva. Domani mattina alle 8:30 il messaggio arriva nel canale.

———

7\) Bonus: Chatbot "Yel" che prenota via chat (5 min, se rimane tempo)

Aggiungi un AI Agent chiamato Yel come componente flottante in basso a destra.

Backend \- crea POST /api/agent:
\- Riceve { messages: ChatMessage\[\] }
\- Chiama OpenRouter con Claude Haiku 4.5 \+ tool calling
\- Tools registrati:
  • get\_rooms() → ritorna le 3 sale
  • get\_bookings(from\_iso, to\_iso) → ritorna prenotazioni nel range
  • create\_booking(room\_name, start\_iso, end\_iso, attendees, purpose, user\_name) → crea prenotazione con conflict check server-side
\- System prompt italiano: "Sei Yel, assistente delle sale Yellow Tech. Prima di prenotare CHIEDI SEMPRE conferma esplicita. Se l'utente dice "domani alle 10" converti in ISO 8601 con TZ Europe/Rome."
\- Loop tool calling fino a max 5 iterazioni

Frontend \- crea ChatWidget.tsx:
\- Bubble flottante "Chiedi a Yel" in basso a destra con dot verde animato
\- Click apre panel 420x620 con header brand (logo \+ nome \+ status), conversation area, input bar
\- 3 suggested prompts iniziali ("Quale sala per 10 persone con proiettore?", "Cosa è prenotato martedì pomeriggio?", "Prenota Sala Cliente domani alle 15…")
\- Tipping indicator con 3 puntini animati durante la chiamata
\- onBookingCreated callback per refresh del calendario

———

Trucchi pro durante la live:

\- Usa Plan Mode di Claude Code per ogni step importante: discute il piano, conferma, poi esegui
\- Quando aggiungi env vars, usa "vercel env add" da CLI: zero click manuali nel browser
\- Per debug Supabase: usa "select \* from pg\_policies where tablename \= 'bookings'" via Management API per verificare le RLS
\- Per il deploy: "vercel deploy \--prod \--yes \--token=$VERCEL\_TOKEN" funziona anche da CI/CD
\- Per n8n: tieni un workflow template salvato, basta cambiare URL \+ webhook

Quando ti blocchi durante la live:

"Sto seguendo il flusso che vediamo insieme. A volte Claude Code chiede conferma su scelte tecniche, vi mostro come decide e procediamo. Va più veloce a farglielo fare che a fermarsi a spiegare ogni riga di codice."

———

Codice completo del tool
GitHub: https://github.com/filippogreco-maker/meeting-room-booking-w4

App live (potete provarla davvero, è in produzione)
https://meeting-room-booking-six-taupe.vercel.app

Workflow n8n (template JSON)
nel repo, cartella /n8n/morning-slack-reminder.json

———
