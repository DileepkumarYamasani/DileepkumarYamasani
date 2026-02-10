# USD Lighting Scene Builder for Houdini Solaris

## 1) System Architecture Overview

The Lighting Scene Builder follows a strict **Component → Compound → Package** workflow so each department stays independent while Lighting gets a coherent, non-destructive stage.

- **Component** (department outputs, versioned)
  - Model USD (geo topology, model variants)
  - Lookdev USD (materials, bindings, shader networks)
  - Animation USD (skeleton, skel animation, xforms, point caches)
- **Compound** (per-asset assembled views)
  - Resolves state + LOD policy
  - Combines model + lookdev + anim in controlled strength order
  - Publishes reusable assembled asset files for shots
- **Package** (shot context)
  - Brings many compounds together
  - Adds shot overrides, lighting layers, render settings
  - Remains inspectable and non-flattened

### Service layers

1. **Context Layer**: show/seq/shot detection, frame range, renderer, unit scale.
2. **Resolver Layer**: asset/version/state/LOD to resolved USD paths.
3. **Validation Layer**: file existence, composition validity, schema compatibility.
4. **Assembly Layer**: generates LOP graph and authored USD layers.
5. **Publish Layer**: writes compound/package artifacts and manifests.

---

## 2) Canonical USD Layout and Naming

A practical filesystem and namespace pattern:

```text
/projects/<show>/assets/<asset>/
  model/publish/v###/usd/model_prim_<state>_lod{0,1,2}.usd
  lookdev/publish/v###/usd/surface_lookdev_<state>_lod{0,1,2}.usd
  anim/publish/v###/usd/rig_anim_<state>_lod{0,1,2}.usd

/projects/<show>/shots/<seq>/<shot>/lighting/
  compounds/<asset>/v###/usd/usd_compound_<state>.usd
  packages/v###/usd/usd_package.usd
  logs/lighting_scene_builder_<timestamp>.log
  manifests/usd_package_manifest.json
```

Recommended root prim conventions:

- Asset root prim: `/Assets/<assetName>`
- Shot root prim: `/Shot`
- Lighting scope: `/Shot/Lighting`
- Render scope: `/Shot/Render`

---

## 3) Composition Strategy (with Strength Rules)

### Composition primitives and intent

- **reference**: Bring a composed asset or department layer onto a prim, reusable and namespaced.
- **payload**: Heavy geometry/rig data for deferred loading and scalable stage performance.
- **sublayer**: Shot-level layering for edit stacks and strongest downstream overrides.
- **variantSet**: Discrete options like `state` and `lod`.

### Strength policy (critical)

Within each asset compound:

1. **Model weakest** (topology/base prim specs)
2. **Animation stronger than model transforms where needed, but weak for lookdev opinions**
3. **Lookdev stronger than model for material bindings and shading opinions**
4. **Shot/lighting overrides strongest at package level**

Practical implementation:

- Keep model/lookdev/anim in separate referenced layers under the same asset root.
- Author lookdev bindings in a stronger local layer than model.
- Keep lighting overrides in shot package sublayers above compounds.

> Note: If animation writes transforms that must override model defaults, anim transform opinions should be stronger than model transforms, while material-related opinions remain dominated by lookdev.

### Non-flattened debug-friendly stack

- Never flatten by default.
- Author sparse override layers per concern (`shot_overrides.usda`, `light_rig_overrides.usda`, `render_settings.usda`).
- Keep published compounds immutable; apply shot-specific deltas upstream in package sublayers.

---

## 4) Component → Compound → Package Data Flow

```text
[Component USDs]
  model_prim_default_lod0.usd
  surface_lookdev_default_lod0.usd
  rig_anim_default_lod0.usd
            |
            v
[Compound Builder]
  - validates paths, prims, variant keys
  - composes /Assets/<asset>
  - authors state and lod variantSets
  - publishes usd_compound_<state>.usd
            |
            v
[Shot Package Builder]
  - references all compounds under /Shot/Assets
  - adds shot overrides sublayer
  - adds /Shot/Lighting and /Shot/Render layers
  - publishes usd_package.usd + manifest
```

### Variant model

- `VariantSet: state = {default, damaged, ...}` on `/Assets/<asset>`.
- `VariantSet: lod = {lod0, lod1, lod2}` either on same root prim or geometry prim.
- Auto LOD mode can be represented with shot-level authored selection policy metadata and/or per-render delegate switch logic.

---

## 5) Solaris LOP Network Strategy

Build a deterministic network with clear zones:

```text
/obj/lopnet1
  CONTEXT
    shot_context (Python LOP/HDA params)
  INGEST
    asset_manifest_import (Python LOP)
    validate_components (Python LOP)
  COMPOUND_<assetA>
    ref_model (Reference LOP)
    ref_anim (Reference LOP)
    ref_lookdev (Reference LOP)
    set_state_variant (Variant LOP)
    set_lod_variant (Variant LOP)
    compound_output (Sublayer/Layer Break)
  COMPOUND_<assetB>
    ...
  PACKAGE
    assemble_assets (Merge LOP)
    shot_overrides (Sublayer LOP)
    lighting_material_library (Material Library LOP)
    render_settings (Render Settings LOP)
    package_output (USD ROP / Layer Save)
```

### Node-creation behavior

- Programmatically create or reuse nodes by stable names (idempotent rebuild).
- Preserve artist-inserted nodes under protected subnet tags.
- Rewire only managed nodes between `BEGIN_MANAGED` and `END_MANAGED` markers.

### Incremental rebuild

- Track node fingerprints (asset + version + state + lod + mode).
- Rebuild only dirty compounds.
- Keep final shot override layers untouched unless explicitly refreshed.

---

## 6) Houdini Tool UX (Python Panel / HDA)

### Core UI modules

1. **Context Bar**: show, sequence, shot (read-only if launched in shot context).
2. **Asset Browser**: searchable list with status badges.
3. **State Selector**: per-asset or bulk (`default`, `damaged`, custom).
4. **LOD Controls**:
   - Manual: per-asset fixed `lod0/1/2`
   - Auto: distance/render-context profile
5. **Version Policy**:
   - Latest approved
   - Pinned from manifest
   - Explicit per department
6. **Build Actions**:
   - Validate only
   - Build compounds
   - Build package
   - Rebuild dirty only

### Artist-safe behavior

- “One-click Build Lighting Scene” creates missing managed nodes only.
- Existing user-authored lights and overrides are not deleted.
- UI warning panel aggregates recoverable failures.

---

## 7) Validation and Error Handling

Validation tiers:

1. **Path/File checks**
   - Missing or unreadable USD
   - Wrong version path pattern
2. **Composition checks**
   - Broken references/payloads
   - Missing default prim
3. **Semantic checks**
   - Variant mismatch (`state` present in model but absent in lookdev)
   - Skeleton/animation compatibility
   - Material binding targets invalid prim paths

Failure policy:

- **Non-blocking by default**: skip invalid asset, continue build.
- **Blocking only for fatal package conditions**: no valid assets, unreadable output target, write failure.

Outputs:

- Real-time UI badges (green/yellow/red)
- Detailed log file with structured error codes
- JSON validation report for farm/publish automation

---

## 8) Pipeline Integration and Scalability

### Asset management integration

- Query asset manager for:
  - Latest approved versions
  - Publish status
  - Department availability
- Persist build manifest:
  - exact resolved component paths
  - hash/fingerprint
  - tool version

### Shot database integration

- Pull shot frame range, handles, camera path, renderer, color pipeline context.
- Drive defaults for LOD auto profiles and render settings.

### Performance/scalability

- Use payloads for heavy geometry and crowd/vegetation assets.
- Defer payload loading in Solaris until look-dev/lighting context requires full expansion.
- Partition compounds by set/dressing categories for parallel updates.
- Cache resolver results to avoid repeated database calls.

### Multi-render delegate support

- Keep renderer-agnostic material interfaces where possible (USDShade standards).
- Delegate-specific overrides in dedicated layers:
  - `render_karma_overrides.usda`
  - `render_arnold_overrides.usda`
  - `render_renderman_overrides.usda`
- Select via shot-level render variant or render settings prim.

---

## 9) Python Implementation Blueprint

```python
class LightingSceneBuilder:
    def __init__(self, hou_lopnet, context, asset_api, shot_api, logger):
        self.lopnet = hou_lopnet
        self.context = context
        self.asset_api = asset_api
        self.shot_api = shot_api
        self.log = logger

    def build(self, request):
        resolved = self.resolve_components(request)
        report = self.validate(resolved)
        compounds = self.build_compounds(resolved, report)
        package = self.build_package(compounds, request)
        self.publish(package, report)
        return package, report

    def resolve_components(self, request):
        # resolve model/lookdev/anim paths by version policy
        pass

    def validate(self, resolved):
        # file checks, usd stage open checks, variant/skeleton checks
        pass

    def build_compounds(self, resolved, report):
        # create/reuse managed LOP nodes per asset
        # set variants and references in deterministic order
        pass

    def build_package(self, compounds, request):
        # merge compounds, add shot override layers, lighting/render layers
        pass

    def publish(self, package, report):
        # write usd package + manifest + logs
        pass
```

### Example: deterministic node upsert

```python
def upsert_lop(parent, node_type, node_name):
    node = parent.node(node_name)
    if node is None:
        node = parent.createNode(node_type, node_name)
    return node
```

### Example: non-destructive managed area

```python
# only edit children between sentinel null nodes:
# BEGIN_MANAGED -> (generated nodes) -> END_MANAGED
# if user nodes exist outside this range, leave untouched.
```

---

## 10) USD Composition Diagram (Layer Stack Example)

```text
usd_package.usd
  subLayers = [
    ./layers/shot_overrides.usda,          # strongest shot opinions
    ./layers/lighting.usda,
    ./layers/render_settings.usda,
    ./layers/assets_assembly.usda          # references compounds
  ]

assets_assembly.usda
  def Scope "Shot" {
    def Scope "Assets" {
      def Xform "CarA" (references = @.../usd_compound_default.usd@) {}
      def Xform "BuildingB" (references = @.../usd_compound_damaged.usd@) {}
    }
  }

usd_compound_default.usd
  def Xform "Assets/CarA" {
    variantSet "state" = "default"
    variantSet "lod" = "lod1"
    references = [
      @model_prim_default_lod1.usd@,
      @rig_anim_default_lod1.usd@,
      @surface_lookdev_default_lod1.usd@
    ]
  }
```

---

## 11) Best Practices for USD Lighting Pipelines

- Keep one concern per layer (model/lookdev/anim/lighting/render settings).
- Enforce strict naming and default prim contracts in publish validation.
- Prefer sparse overrides; avoid authoring broad xform/material edits in package unless needed.
- Use manifests to guarantee reproducibility and easy rollback.
- Build idempotent tools: running twice should not duplicate nodes or opinions.
- Expose composition diagnostics directly in artist UI (what file, what layer, what prim).

---

## 12) Common Pitfalls and Mitigations

1. **Variant drift across departments**
   - Mitigation: centralized variant dictionary and publish-time schema checks.
2. **Over-strong animation layers overriding lookdev unintentionally**
   - Mitigation: separate opinions by prim/property scope and enforce layer order tests.
3. **Unbounded payload loading in heavy shots**
   - Mitigation: payload policy profiles and viewport-purpose defaults.
4. **Destructive rebuilds wiping artist edits**
   - Mitigation: managed subnet boundaries + immutable user layer policy.
5. **Renderer-specific shader fragmentation**
   - Mitigation: common material contracts + delegate override layers only where required.

---

## 13) Recommended Deliverables for Production Rollout

1. Houdini HDA/Python Panel (`Lighting Scene Builder`) with context-aware UI.
2. Builder backend Python package with resolver, validator, assembler, publisher modules.
3. USD schema contract document for Component/Compound/Package.
4. CI validation scripts for publish gates.
5. Onboarding documentation and debug playbook for Lighting TDs.

This design keeps assembly transparent, scalable, and resilient while preserving USD composition semantics and artist-friendly workflows.
