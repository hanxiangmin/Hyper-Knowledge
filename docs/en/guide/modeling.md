# Entities, events, and roles

The modeling goal is to **keep the participants, conditions, and evidence of one event attached to the same relationship**. A hyperedge is useful because its context is inspectable, not simply because it can be drawn as a large enclosure.

## An entity answers “what is it?”

People, places, dates, works, and organizations are reusable entities. A label identifies an object, a type describes its category, and an identifier distinguishes it from objects with the same name.

In the repository example, “1101 return-to-Changzhou stage” should not be a composite entity:

| Representation | Content | Purpose |
| --- | --- | --- |
| Person node | Su Shi | Reusable across events |
| Time node | 1101 | Independently referable date |
| Place node | Changzhou | A location with its own identity |
| Hyperedge predicate | Return north | The event being represented |
| Member roles | Returning person, time, destination | Participation within this event |

This describes the example's modeling choice, not a new historical claim.

## A hyperedge answers “what brings them together?”

The Three Su family, an examination, and the Wutai Poetry Trial are different contexts. Sharing a person is not a reason to merge them into one large relationship.

A useful hyperedge has a specific predicate, a member set, and interpretable roles. Its members need not share one uniform pairwise relation: a date and an examiner simply participate in the same examination event.

## A role answers “how does this member participate?”

Roles belong to memberships, not to a person's permanent identity. Su Shi can be an examination candidate in one relation and a defendant or administrator in another.

If one relation contains several dates or places, first ask whether multiple events have been mixed together:

- Split separate episodes into event hyperedges that share the person.
- For multiple dates within one event, use specific roles such as start and end.
- If the source does not explain how the values correspond, retain uncertainty instead of pairing them by guesswork.

The biography example separates exile in Huizhou, exile in Danzhou, and the return north. This keeps dates attached to their respective places and events.

## A shared node does not create a new fact

Appearing in 18 hyperedges is a membership count. Central positioning, a larger circle, and crossing enclosures are display choices, not additional assertions. Dragging and zooming change the reading experience only.

Compact display labels may omit matching outer quotation or title marks; the stored label and detail panel retain the original. Disambiguate works, editions, and names with identifiers and properties rather than arbitrary truncation.

Next: [inspect these choices in the Su Shi example](sushi.md).
