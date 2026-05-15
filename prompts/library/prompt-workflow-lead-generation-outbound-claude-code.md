---
id: prompt-workflow-lead-generation-outbound-claude-code
name: Prompt Workflow per lead generation e outbound con Claude Code
type: prompt
status: stable
version: 1.0.0
description: Workflow di prompt per lead generation e campagne outbound con Claude Code e skill GTM
tags: [workflow, claude-code, italian, lead-generation, outbound]
language: it
created: 2026-05-16
updated: 2026-05-16
author: riccardo
---
# Prompt Workflow per lead generation e outbound con Claude Code

Filippo Greco · Yellow Tech

A cosa serve questo file:

Questo documento raccoglie i prompt e i comandi delle skill utilizzati durante il secondo webinar della Claude Week di Learnn ("Claude Code per il GTM", 6 maggio 2026).

**Per replicare la demo**:

1. Scarica gli zip delle skill linkate qui sotto
2. Scompattali nella tua cartella \~/.claude/skills/ (o nel folder skills del tuo progetto)
3. Apri Claude Code
4. Copia ed esegui i prompt in ordine partendo dal CLAUDE.md.

Skill da installare su Claude:

* [/skill-builder](https://learnn.com/template/?content_id=e5aJekQ) (Claude Skill per creare nuove Skill partendo da idee e task ripetitivi)
* [/lead-enrichment](https://learnn.com/template/?content_id=PR518Jx) (Claude Skill per trasformare liste lead incomplete in prospect qualificati)
* [/outbound-campaign](https://learnn.com/template/?content_id=jeQ6koJ) (Claude Skill per creare campagne outbound personalizzate)
* [/trend-analysis](https://learnn.com/template/?content_id=X5WJN7j) (Claude Skill per analizzare trend di mercato e competitor)

──────────────────────────────────────────────────────

1\) CLAUDE.md (file di memoria persistente — Bullet 1\)

\# Chi sono
Filippo Greco, GTM Engineer @ Yellow Tech.
Costruisco pipeline GTM da zero per Yellow Tech e per clienti.

\# Stack
\- SmartLead per email campaigns
\- HeyReach per LinkedIn outreach
\- Attio come CRM
\- Clay \+ parallel-cli per enrichment
\- Google Sheets per le liste lead

\# Tono
Diretto, operativo, no fluff.

──────────────────────────────────────────────────────

2\) Test MCP (Bullet 1\)

Leggi le ultime 5 email da info@learnn.com e dimmi di cosa parlano in 3 bullet ognuna.

──────────────────────────────────────────────────────

3\) /skill-builder (Bullet 2\)

/skill-builder

──────────────────────────────────────────────────────

4\) /lead-enrichment (Bullet 3\)

/lead-enrichment \<sheet-url\>

──────────────────────────────────────────────────────

5\) /outbound-campaign (Bullet 4\)

/outbound-campaign \<sheet-url\> \--target=hot \--sequence=4-touch

──────────────────────────────────────────────────────

6\) /trend-analysis (Bullet 5\)

/trend-analysis \<competitor-list\> \--window=30d \--signal=topics,engagement,format
