---
status: "Proposed"
date: YYYY-MM-DD
deciders: [list everyone who weighs in on the decision]
consulted: [optional — subject-matter experts consulted]
informed: [optional — people kept up to date]
tags: []                 # array of topic tags, e.g. [database, infra]
continuation_of: []      # optional — ADR stem(s) this one continues, validated
                         # to exist, e.g. [20260801-caching]
group: ""                # optional — iteration slug shared by related ADRs;
                         # also used as the <group> segment in the grouped filename
---

# 📝 Short title of the decision

> ADR **YYYYMMDD-title** · this is the **summary** (the decision).
> Related: [plan](YYYYMMDD-title-1-plan.md) · [follow-ups](YYYYMMDD-title-2-followups.md).
> Keep this file under **350 lines**.

## 🚦 Status

Proposed

<!--
Allowed values: Proposed | Accepted | Rejected | Deprecated | Superseded
When superseding, write: "Superseded by [YYYYMMDD-title](YYYYMMDD-title-0-summary.md)".
`adrs:init` always creates the summary as Proposed. Transitions happen via `adrs:update`.
-->

## 🧭 Context and Problem Statement

Describe the context and problem in two or three sentences. What is forcing a
decision now? You may state the problem as a question. Link prior ADRs this
supersedes or builds on.

## 📋 Requirements

The requirements and constraints the decision must satisfy — these are the
criteria the options are judged against.

* Requirement 1 — a functional need, constraint, or quality attribute
* Requirement 2 — e.g. a cost ceiling, performance target, or team concern

## ⚖️ Considered Options

* Option 1 — short name
* Option 2 — short name
* Option 3 — short name

## ✅ Decision Outcome

Chosen option: "Option N", because <justification — how it best satisfies the
requirements>.

### Pros and Cons of the Options

#### Option 1 — short name

* Good, because <argument>
* Bad, because <argument>

#### Option 2 — short name

* Good, because <argument>
* Bad, because <argument>

## 📌 Consequences

* Good, because <positive consequence of the chosen option>
* Bad, because <negative consequence or trade-off accepted>
