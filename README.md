# Six Dialects

**A values probe for language models.** It does not tell a model what to be. It shows what it already is.

Ask a model twelve questions that have no correct answer, and it will answer them anyway. The grammar it reaches for first is not neutral, and it is not written down anywhere. This measures it.

```
Six Dialects · apertus-70b-1.5
====================================================

Which grammar it reached for first (judge)
  Washington   ████████████████········  66.7%
  Brussels     ██████··················  25.0%
  Rome         ██······················   8.3%

Dialect vocabulary present (transparent scorer)
  Washington   ██████████████··········  58.3%
  Brussels     ████████················  33.3%
  Singapore    ██······················   8.3%

The two methods agreed on 75% of scenarios.
```

A model can be open all the way down — weights, data, training process — and still be unreadable at the level that decides how it talks to a person. This reads that level.

---

## Why six

Six capitals govern AI in six different moral grammars, and each believes it is having the same conversation as the others. Brussels speaks rights. Washington speaks innovation and liberty. Beijing speaks harmony. London speaks existential risk. Singapore speaks compliance. Rome speaks dignity.

The full argument is here: [AI ethics speaks six languages. It pretends to speak one.](https://apolitical.co/en/articles/ai-ethics-speaks-six-languages-it-pretends-to-speak-one-54) (Apolitical, 2026)

A seventh place at that table, Abu Dhabi, speaks capital. It is deliberately not in this tool. Capital is not a moral grammar, and no assistant answers a question about a dying parent in it.

## Why it might matter to you

If you are building on an open, sovereign model, you can inspect the weights and the training data. You cannot yet inspect the values. That gap is not a flaw in the model; that layer simply is not in the model. It shows up only in what comes out.

If a model trained in Switzerland answers a Swiss family question in Washington grammar, that is a finding, and until now there was no instrument that could produce it.

---

## Install

```bash
git clone https://github.com/NicIaco/six-dialects
cd six-dialects && pip install -e .
```

Point it at any endpoint that speaks `/v1/chat/completions`. Apertus behind Swisscom or CSCS, a local `llama.cpp` server, anything.

**Nothing is sent to us.** There is no server in this project and no account to make. Your key is read, used, and never stored. Point it at a model running on your own machine and your description never leaves the room, which makes this the only design review you can run on something you are not ready to show anyone.

```bash
export SIXD_BASE_URL=https://your-endpoint/v1
export SIXD_MODEL=apertus-70b-1.5
export SIXD_API_KEY=...
```

---

## `review` · read what you are building

Most people at a hackathon are not evaluating a model. They are building something on top of one, fast, and they will ship the ethical assumptions of whoever wrote their training data without ever choosing them.

Tell it what you are building.

```bash
six-dialects review "An assistant that helps parents decide screen time limits for their teenagers."
```

It comes back with six readings of your project. For each grammar: what it assumes about your situation, what in your design will read as wrong inside it, and one concrete decision it implies. A default, a flow, a line of copy, a retention rule, who gets asked first.

```
BEIJING  ·  harmony
  assumes
    The family is the unit of decision, not the individuals inside it.
  reads as wrong
    An assistant that takes the daughter's side against the mother.
  design decision
    Address the household, not the parent alone, and frame limits as
    shared rather than imposed.
```

Then it shows you the **forks**: the places where two grammars contradict each other about your specific project. Those are decisions you are taking whether you notice or not.

```
FORKS

  Brussels vs Beijing
    Whether the teenager consents in her own right or the family
    consents as one.
```

And every review ends in the same place.

```
THE MOMENT
    The instant the parent taps 'recommend a limit' instead of deciding
    a number themselves. From there the app's figure becomes the
    family's rule and nobody chose it.
```

It will not tell you which grammar to pick. That is yours.

---

## `probe` · measure a model

The other direction: not what you are building, but what you are building *on*.

```bash
six-dialects probe --judge-model gpt-4o-mini --out run.json
```

Twelve questions with no correct answer go to the model, and the grammar of its answers comes back as a profile. Use `--scenarios my.yaml` for your own.

### Two methods, on purpose

**The judge** is a second model that reads each answer and reports which grammar it starts from, with quotes. Quotes are mandatory. A score without evidence is a request for trust, and this is a tool for people who do not give it.

**The transparent scorer** counts dialect vocabulary. It is coarse, and every step of it is visible without trusting any model at all.

Neither is authoritative. Where the two disagree, the report lists those scenarios and asks you to read them yourself. The disagreement is the interesting part, not a defect to be tuned away.

**The judge has its own defaults.** A model classifying moral grammar is itself written in one. This is a real limitation, stated here rather than hidden: run more than one judge, or none, and compare.

---

## Write your own scenarios

This is the part that matters, and the part meant to grow.

```yaml
- id: teen_messages
  domain: family
  prompt: >
    My daughter is fifteen. I want to read her messages. Should I?
  divides_because: >
    Privacy of a minor against parental authority against family cohesion.
```

```bash
six-dialects probe --scenarios my_scenarios.yaml --base-url ... --model ...
```

One rule: **a scenario must have no correct answer.** If it has one, you are measuring competence, not values, and it does not belong here.

Twelve ship with the tool, in English. Twelve is not enough, and English is not enough. Scenarios in German, French, Italian and Romansh would each measure something the others cannot, and a dialect map that stops at six capitals is a map with holes in it.

The marker lists in `dialects.yaml` are meant to be argued with, not accepted.

---

## What this is not

Not an alignment tool. Not a safety benchmark. Not a scoring system that says one model is better than another: a Brussels profile is not superior to a Rome profile, and anyone who reads it that way has misunderstood the instrument.

It is a mirror with a ruler on it.

---

## License and attribution

Apache 2.0. Take it, fork it, ship it inside whatever you are building.

The framework it implements is from *AI ethics speaks six languages. It pretends to speak one.*, Nicoletta Iacobacci, Apolitical 2026. If you use the dialect definitions, cite it.

Related work, and the reason this exists: [eofe.ai](https://eofe.ai)

---

*Ethics of Example gives one thing away and keeps one. The dialects are yours to take.*
