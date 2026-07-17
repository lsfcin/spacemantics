# tests
> ← add description

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`conftest.py`](conftest.py) | [`conftest.pyi`](conftest.pyi) | `build`, `make_scene`, `degrees` | Scene fixtures: a definite desk/chair/lamp/ball scene in canonical form, built through the loader. |
| [`test_declarations.py`](test_declarations.py) | [`test_declarations.pyi`](test_declarations.pyi) | `document_without`, `test_a_missing_tolerance_does_not_parse`, `test_a_missing_frame_does_not_parse`, `test_a_non_canonical_frame_is_rejected_at_the_door`, `test_the_type_ontology_is_user_extensible` | The header is mandatory: no frame, no tolerance, no non-canonical frames. Plus the user-extensible type ontology. |
| [`test_direction.py`](test_direction.py) | [`test_direction.pyi`](test_direction.pyi) | `verdicts`, `test_world_anchor_needs_no_frame`, `test_locale_anchor_reads_the_grounds_own_front`, `test_locale_on_a_frontless_ground_is_an_error`, `test_projective_term_without_any_frame_is_an_error` | DIR under the three anchors, and the arity gate: an unreadable projective term is an ERROR, never a FAIL. |
| [`test_metrics.py`](test_metrics.py) | [`test_metrics.pyi`](test_metrics.pyi) | `only`, `test_distance_is_point_to_region`, `test_distance_can_fail`, `test_ordinal_quantity_in_a_metric_predicate_is_a_type_error`, `test_grid_units_need_a_declared_cell_size` | DIST, faces, alignment — and the ordinal rule: rank may never enter a metric predicate (C2). |
| [`test_quantifiers.py`](test_quantifiers.py) | [`test_quantifiers.pyi`](test_quantifiers.pyi) | `only`, `test_no_two_objects_overlap`, `test_an_overlap_is_caught_with_its_witness`, `test_count_stops_the_delete_everything_strategy`, `test_every_binds_the_figure_over_a_set` | Coverage and negation: without them a checker gets gamed (a baseline "solved" scenes by deleting objects). |
| [`test_temporal.py`](test_temporal.py) | [`test_temporal.pyi`](test_temporal.pyi) | `scene_with`, `test_pose_is_interpolated_at_the_stated_instant`, `test_the_same_claim_fails_later`, `test_hold_is_a_sampled_invariant`, `test_hold_reports_where_it_broke` | Time: keyframed poses, HOLD as a sampled invariant, Allen over events — and the ordinal-timebase type error (C3). |
| [`test_topology.py`](test_topology.py) | [`test_topology.pyi`](test_topology.pyi) | `box`, `test_relation_codes`, `test_inverse_codes`, `test_inside_is_not_within`, `test_tolerance_decides_contact_versus_gap` | RCC-8 must produce all eight codes on definite regions, and 'is inside' must genuinely differ from 'is within'. |
<!-- routing:end -->
