# Six Dialects

**A framing probe for language models.** It does not tell a model what to be, and it does not claim to see inside one.

Ask a model twelve questions that have no correct answer, and it will answer them anyway. Every answer starts somewhere: from a right, from a freedom, from the stability of a group, from a rule. This reads where the answer starts, and reports it.

It classifies the ethical premise a model's answer is written from. It does not observe latent values, weights or reasoning. Nothing here has access to anything but text that came out.

```
Six Dialects · apertus-70b-1.5
====================================================

Ethical premise the answer starts from (judge)
  Washington   ████████████████········  66.7%
  Brussels     ██████··················  25.0%
  Rome         ██······················   8.3%

Dialect vocabulary present (marker count)
  Washington   ██████████████··········  58.3%
  Brussels     ████████················  33.3%
  Singapore    ██······················   8.3%

The two readings coincided on 75% of scenarios.
(internal cross-check, not validation: see below)
```

A model can be open all the way down, weights and data and training process, and still be unreadable at the level that decides how it talks to a person. This reads that level, imperfectly, from the outside.

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

### Tell it more and it reads better

A one-line description leaves the model to guess who is at the keyboard and who has to live with the result, and it guesses badly. Four optional fields close that gap:

```bash
six-dialects review "A tool that ranks residential buildings for public retrofit funding." \
  --used-by "a council clerk preparing the agenda" \
  --affects "residents of the buildings being ranked" \
  --region  "Swiss municipalities, German and French" \
  --decides "the order in which buildings receive public money"
```

`--affects` is the one that earns its place. The operator and the affected party are usually different people, and a grammar that protects one often does not protect the other. Said out loud, that difference is most of the reading.

`--decides` is what makes the delegation moment findable. Name the output a human acts on, and the tool can find the point where they stopped weighing it.

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

**They are not independent, and their agreement is not validation.** Both are built from the same six definitions in `dialects.yaml`: the judge reads `starts_from`, the marker count reads `markers`. When they coincide, that is two operationalisations of one schema agreeing with each other, which is internal consistency and nothing more. It is reported because disagreement is diagnostic, not because agreement is evidence.

Where the two diverge, the report lists those scenarios and asks you to read them yourself. That divergence is the useful part.

**The judge has its own defaults.** A model classifying moral grammar is itself written in one. This is a real limitation, stated here rather than hidden: run more than one judge, or none, and compare.

---

## What has not been validated

This is the honest limit of the instrument, stated here rather than discovered by someone else.

**There is no independent ground truth.** The six categories were defined by one person, the scenarios were written to separate those same categories, and the judge is handed those same definitions and asked which one it sees. Read strictly, the repository currently demonstrates that model answers *can be read coherently* through this lens. It does not yet demonstrate that the six categories measure anything about a model that another method would also find.

What would fix it, in order:

1. **Blind human annotation.** Three to five people who know the framework label the same corpus of outputs without seeing each other's labels or the judge's.
2. **Inter-annotator agreement.** If humans do not converge, the categories are not yet a measure, and that is worth knowing.
3. **Judge against human consensus**, rather than judge against keyword count.

Until that exists, treat every number this tool prints as a reading, not a measurement.

**This is the most useful thing anyone could contribute.** Building the annotated corpus is a real piece of work and it does not require writing any code: it requires several people reading model outputs carefully and disagreeing with each other in writing. If you do it, open a pull request with the labels and the disagreements, both.

**The marker count is naive by construction.** It counts words. It does not handle negation: "the family should not decide this" contains *family* and will push the text toward Beijing. Several markers are also generic enough to appear in any framing. Both are known and neither is hidden; the count is there to be checkable, not to be right.

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
