# Topic Taxonomy — 50 topic comuni per settore B2B/B2C

Per clustering semantic delle conversazioni social. Quando analizzi contenuti competitor, mappa ogni post a UNO di questi topic.

## B2B SaaS / Tech

### Go-to-Market
1. **Lead generation strategies**
2. **Outbound prospecting tactics**
3. **Pricing & packaging**
4. **Sales process optimization**
5. **Customer acquisition cost (CAC) reduction**
6. **Product-led growth**
7. **Partner channel strategies**
8. **Account-based marketing (ABM)**

### Product
9. **Feature launches**
10. **User feedback & iteration**
11. **Product-market fit stories**
12. **Integration ecosystem**
13. **API & developer experience**

### Team & culture
14. **Hiring (specific roles)**
15. **Remote work culture**
16. **Founder journey (personal)**
17. **Failures & learnings**

### Metrics & data
18. **Growth metrics transparency**
19. **Retention & churn**
20. **NPS & customer satisfaction**

## Marketing

21. **Content marketing strategy**
22. **SEO tactics**
23. **Paid ads optimization (Meta, Google)**
24. **Social media algorithm hacks**
25. **Email marketing**
26. **Branding & positioning**
27. **Influencer partnerships**

## AI / Tech commentary

28. **AI tools for productivity**
29. **LLM prompts & techniques**
30. **AI agents & automation**
31. **No-code/low-code stacks**
32. **Developer tooling**

## Leadership & management

33. **Management lessons**
34. **Hiring & firing**
35. **OKRs & goal setting**
36. **Difficult decisions**

## Finance / fundraising

37. **Fundraising stories**
38. **Bootstrapping journey**
39. **Financial model transparency**
40. **Exit stories (acquisition, IPO)**

## Industry specific

### EdTech
41. **Course creation process**
42. **Student engagement tactics**
43. **AI in education**

### E-commerce
44. **Conversion rate optimization**
45. **Logistics & fulfillment**
46. **DTC brand building**

## Generic engagement patterns

47. **Contrarian opinions**
48. **Behind-the-scenes**
49. **Industry predictions**
50. **Tool comparisons / reviews**

## Come usare la taxonomy

### Match semantico

Per ogni post estratto:
```python
prompt = f"""
Given this social post:
{post_text}

Map it to ONE topic from this taxonomy:
{taxonomy_numbered_list}

Output only the topic number (1-50) and a confidence 0-1.
Example: "17, 0.85"
"""
```

### Aggregazione

```python
from collections import Counter
topic_counts = Counter()
topic_engagement = Counter()

for post in posts:
    topic_id = classify(post)  # via LLM
    topic_counts[topic_id] += 1
    topic_engagement[topic_id] += post['reactions']

# Top topic per pure volume
top_volume = topic_counts.most_common(10)

# Top topic per engagement (quello che funziona davvero)
top_engagement = topic_engagement.most_common(10)
```

### Insight

Confronta `top_volume` vs `top_engagement`:
- **Topic in volume alto ma engagement basso**: competitor posta ma pubblico non reagisce → opportunità di NON seguire il trend
- **Topic in engagement alto ma volume basso**: underserved → opportunità a tuo vantaggio
- **Topic in entrambi**: mercato saturato ma funzionante → attacca con angolo differente

## Estensione

Se il settore non è coperto (es. healthtech, proptech, legaltech), estendi con 10-15 topic verticali.
Mantieni ID numerici stabili per confronto longitudinale.
