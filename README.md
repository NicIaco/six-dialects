# Six Dialects

**AI ethics is not written in one language. It is written in six, and they are not the same one.**

Brussels reasons from rights. Washington from liberty. Beijing from the stability of the group. London from catastrophic risk. Singapore from compliance. Rome from human dignity. Each believes it is having the same conversation as the others, and each starts somewhere the others do not.

*The argument this comes from: [AI ethics speaks six languages. It pretends to speak one.](https://apolitical.co/en/articles/ai-ethics-speaks-six-languages-it-pretends-to-speak-one-54), Apolitical 2026, and in Italian in [Il Mondo Nuovo](https://www.ilmondonuovo.club/letica-dellai-parla-sei-lingue-e-fa-finta-di-parlarne-una/).*

This is an instrument for reading which of those six a piece of reasoning comes from. It does not tell a model what to be, and it does not claim to see inside one.

Ask a model twelve questions that have no correct answer, and it will answer them anyway. Every answer begins somewhere. This reads where, and reports it.

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

Rome is the tradition of human dignity, from Rerum Novarum to the Rome Call and the 2026 encyclical. Not the Treaty of Rome: that grammar is Brussels.

The full argument is here: [AI ethics speaks six languages. It pretends to speak one.](https://apolitical.co/en/articles/ai-ethics-speaks-six-languages-it-pretends-to-speak-one-54) (Apolitical, 2026), and in Italian: [L'etica dell'AI parla sei lingue. E fa finta di parlarne una.](https://www.ilmondonuovo.club/letica-dellai-parla-sei-lingue-e-fa-finta-di-parlarne-una/) (Il Mondo Nuovo, 2026)

A seventh place at that table, Abu Dhabi, speaks capital. It is deliberately not in this tool. Capital is not a moral grammar, and no assistant answers a question about a dying parent in it.

**Six is a sample, not a census.** The set can gain a dialect and it can lose one, and both take evidence rather than argument. See [how a dialect gets in, and how one gets out](#how-a-dialect-gets-in-and-how-one-gets-out).

---

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

## Related work, and what is different here

The field has been mapped carefully, and it has been mapped along a different axis.

**Jobin, Ienca and Vayena (2019)** surveyed 84 AI ethics documents and found a global convergence around five principles: transparency, justice and fairness, non-maleficence, responsibility, privacy. In the same abstract they record what the convergence conceals: *substantive divergence in relation to how these principles are interpreted, why they are deemed important, what issue, domain or actors they pertain to, and how they should be implemented.*
[Nature Machine Intelligence 1, 389–399](https://doi.org/10.1038/s42256-019-0088-2)

**Corrêa et al. (2023)** extended the survey to 200 guidelines and found 17 recurring principles, with transparency in 86% of documents and justice in 81%. The picture holds at scale: everyone signs the same words.
[Patterns 4(10)](https://doi.org/10.1016/j.patter.2023.100857)

Both count **what documents state**. That is the right thing to count if you want to know whether the field has agreed on a vocabulary. It has.

This tool counts something else: **the premise an argument starts from.** Not which principles a text names, but where its reasoning begins when the principles collide, which they always do in any real case. Two answers can both invoke transparency and start from irreconcilable places: one from the right of the person affected, one from the freedom of the person deciding.

So the relation is not disagreement. Jobin and colleagues named the divergence and left it as residue, because their instrument was built to measure convergence. Six Dialects takes that residue as the object.

### The premise has been named, but not turned into an instrument

Two papers get closer than the surveys do, and neither is a competitor. Both are prior work this depends on.

**Donahoe and Metzger (2019)** argue for human rights as the frame for AI governance, against the alternatives. That is an argument *from* a premise, made well, rather than a classification *of* premises.
[Journal of Democracy 30(2), 115–126](https://doi.org/10.1353/jod.2019.0029)

**Wong (2020)** is the closest, and the most important one here. He examines what happens when cultural difference is offered as a reason to hold AI to a different ethical standard, and asks when that is a legitimate claim about values and when it is a licence.
[Philosophy & Technology 33, 705–715](https://doi.org/10.1007/s13347-020-00413-8)

**Wong's paper is also a warning aimed squarely at this project, and it should be read that way.**

A tool that says "Beijing starts from the stability of the group" can be picked up and used to argue that a system built there should not be held to the same standard. That is precisely the move Wong is against, and it would be a straightforward misuse of this instrument.

So, stated plainly: **describing a grammar is not endorsing it.** This tool reports where an argument begins. It does not say that all beginnings are equally defensible, and nothing in it licenses treating a rights violation as a dialect. A grammar can be accurately described and still be wrong.

### What this leaves as the claim

The premise axis exists in the philosophical and policy literature. What does not exist, as far as I can find, is any instrument that classifies by premise and applies it to what AI systems actually output rather than to what governance documents state.

That is the gap this occupies: not a new idea about ethics, but a measurement applied where the existing taxonomies were never pointed.

An unoccupied axis is not a correct one. It can be empty because it is a bad idea, and whether this one cuts anywhere useful is exactly what the [validation work](#what-has-not-been-validated) would establish.

If you know of prior work that classifies by premise, or that has done this to model outputs, it belongs here. Open an issue.

---

## How a dialect gets in, and how one gets out

Six is a sample, not a census. The claim was never that there are exactly six moral grammars. It is that there is more than one, and that pretending there is a single shared language is the first error, the one the others descend from.

So the set has to be able to move. A taxonomy that cannot change is the same frozen snapshot this project exists to argue against, moved up one level: not the rules frozen, but the categories.

It also has to be able to move in both directions, or it is a collection rather than a measure.

### Admission

A candidate enters only if it is **not reducible to a variant of one already here.**

The test is discriminative and it is run, not argued:

1. Write scenarios where you expect the candidate to answer differently from all six.
2. Run them. Include the outputs.
3. Show where the existing six converge and the candidate does not.

An accent is not a dialect. If the candidate's answers can be read as one of the six with different vocabulary, it is vocabulary.

Open a pull request with the scenarios, the runs and the proposed definition. Evidence, not advocacy.

### Removal

If two of the six **never diverge** across a substantial scenario set, they are one dialect wearing two names, and they should be merged.

Two are already worth suspecting, and this is not modesty:

- **Brussels and Singapore** are both proceduralisms. One proceduralises rights, the other compliance. If no scenario separates them, that is one grammar.
- **London and Washington** come from the same Anglo-American liberal frame. Existential risk may be a dialect of liberty rather than a language of its own.

A merge proposal takes the same form as an admission: scenarios, runs, and the evidence that no separation appears.

### When nothing fits

If a case cannot be described by any of the six, **record the failure rather than adding a box to absorb it.**

Frameworks do not usually die of being wrong. They die by accretion: each addition is reasonable, and after two years there are fourteen categories and no thesis. A documented gap is worth more than a seventh category invented to close it.

### Currently under consideration

- **Ubuntu.** Relational personhood, from southern African philosophy, with a real body of AI governance work behind it. Not the same as Beijing: there, what matters is the stability of the group; here, that a person exists only inside their relations.
- **Delhi.** Obligation arising from the role one occupies, rather than from a right held or an order to be kept.
- **Aotearoa.** Governance through a treaty relationship and guardianship rather than ownership.
- **Abu Dhabi.** Named in the article as a seventh place at the table, and deliberately kept out of this tool: capital is not a moral grammar, and no assistant answers a question about a dying parent in it. That exclusion is a judgment, not a fact, and it is written here so that someone can argue with it.

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

Not a compliance tool. It does not tell you whether you comply; it shows you what you are assuming, so that you know what to go and check.

Not an alignment tool. Not a safety benchmark. Not a scoring system that says one model is better than another: a Brussels profile is not superior to a Rome profile, and anyone who reads it that way has misunderstood the instrument.

It is a mirror with a ruler on it.

---

## License and attribution

Apache 2.0. Take it, fork it, ship it inside whatever you are building.

Six Dialects was created and is maintained by Nicoletta Iacobacci, [ORCID 0000-0003-0274-4049](https://orcid.org/0000-0003-0274-4049). Copyright 2026.

The framework it implements is from [*AI ethics speaks six languages. It pretends to speak one.*](https://apolitical.co/en/articles/ai-ethics-speaks-six-languages-it-pretends-to-speak-one-54), Nicoletta Iacobacci, Apolitical 2026, also published in Italian in [Il Mondo Nuovo](https://www.ilmondonuovo.club/letica-dellai-parla-sei-lingue-e-fa-finta-di-parlarne-una/). If you use the dialect definitions, cite it.

If you use the tool itself, cite the archived release:

[![DOI](https://zenodo.org/badge/1344814136.svg)](https://doi.org/10.5281/zenodo.22145171)

**The name.** Apache 2.0 grants copyright and patent rights, and does not grant trademark rights. Fork the code freely. If you distribute a modified version, give it a different name, so that readers can tell your work from this one. Describing your project as "based on Six Dialects" needs no permission.

Related work, and the reason this exists: [eofe.ai](https://eofe.ai)

---

*Ethics of Example gives one thing away and keeps one. The dialects are yours to take.*
