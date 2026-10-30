"""Feed ontology contribution (CONCEPT:AU-KG.ontology.package-federation-migration).

Data-only subpackage: it carries ``feed.ttl`` (the ``owl:Ontology``
``http://knuckles.team/kg/feed`` module — feed sources, RSS feeds, feed items
and their relationships) which the scion-sdk hub federates in via the
``scion_sdk.ontology_providers`` entry-point. It holds no business logic
and no heavy imports so the hub can resolve it cheaply.
"""
