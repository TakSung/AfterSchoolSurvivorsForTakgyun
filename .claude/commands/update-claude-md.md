# Update CLAUDE.md Command

## Purpose
Efficiently update CLAUDE.md with minimal token usage by leveraging existing rules and commands through reference patterns.

## Usage
```
/update-claude-md <specific_change_description>
```

## Advanced Prompt Engineering: Incremental Update Pattern

### Step 1: Change Impact Analysis
**CRITICAL: Use Chain-of-Thought reasoning to minimize changes**

```
Before making ANY changes, analyze:
1. 🎯 SCOPE: What specific section needs updating?
2. 📋 EXISTING: What rules/commands already exist in .claude/commands/?
3. 🔗 REFERENCE: Can this be solved with @references instead of duplication?
4. 🪶 MINIMAL: What's the smallest change that achieves the goal?
```

### Step 2: Reference-First Strategy (Token Optimization)

**Priority Order:**
1. **@Reference Pattern**: Link to existing .claude/commands/ files
2. **Inline Micro-Updates**: Add 1-3 lines maximum 
3. **Section Addition**: Only if no existing reference possible

```python
# ✅ PREFERRED: Reference existing commands
**Korean Testing:** @/.claude/commands/write-unit-test.md
**Rule Creation:** @/.claude/commands/write-rule.md

# ❌ AVOID: Duplicating existing content
"""
### Korean Testing Pattern
[500+ lines of duplicated content from write-unit-test.md]
"""
```

### Step 3: Surgical Update Protocol

**Micro-Update Template:**
```markdown
# Add this pattern for small additions:
### [Section Name]
**KEY_CONCEPT**: Brief explanation (max 2 lines)
**Reference**: @/.claude/commands/specific-command.md
```

### Step 4: Validation Checklist

Before finalizing updates:
- [ ] Can this be solved with @reference instead?
- [ ] Is the change under 10 lines total?
- [ ] Does it avoid duplicating existing .claude/commands/ content?
- [ ] Will this reduce future token usage?

## Update Categories & Patterns

### Category A: New Concept Introduction
```markdown
# Pattern: Minimal introduction + Reference
### [New Concept Name]
**Purpose**: One-line description
**Implementation**: @/.claude/commands/new-command.md
```

### Category B: Existing Rule Enhancement
```markdown
# Pattern: Enhance existing section with reference
**Enhanced [Feature]**: Brief update (max 1 line)
**Details**: @/.claude/commands/enhanced-rule.md
```

### Category C: Project-Specific Integration
```markdown
# Pattern: Context bridge to existing commands
### AfterSchoolSurvivors Integration
**Game-Specific Rules**: @/.claude/rules/game-development.md
**ECS Testing**: @/.claude/commands/write-unit-test.md#ecs-patterns
```

## Anti-Patterns to Avoid

```python
# ❌ WRONG: Large content blocks
"""
Adding 200+ lines of new testing rules directly to CLAUDE.md
when they should be in .claude/commands/write-unit-test.md
"""

# ❌ WRONG: Duplicating existing commands
"""
Copying entire sections from existing .claude/commands/ files
"""

# ❌ WRONG: Generic massive updates
"""
Rewriting entire sections when only 2-3 lines need changes
"""

# ✅ CORRECT: Minimal reference-based updates
"""
**New Feature**: Brief description
**Guide**: @/.claude/commands/new-feature.md
"""
```

## Advanced Techniques Applied

### 1. **Retrieval-Augmented Generation (RAG)**
- Check existing .claude/ structure before adding
- Reference existing content instead of duplicating

### 2. **Few-Shot Learning Pattern**
- Provide 2-3 examples of good vs bad updates
- Show minimal change patterns

### 3. **Chain-of-Thought Reasoning**
- Force analysis before changes
- Validate necessity of each update

### 4. **Context Compression**
- Use @references for token efficiency
- Maintain context through minimal bridges

## Command Execution Flow

```python
def update_claude_md(change_description: str):
    # 1. Analyze existing .claude/ structure
    existing_commands = scan_claude_directory()
    
    # 2. Determine if reference pattern applicable
    if can_reference_existing(change_description):
        return create_reference_update(change_description)
    
    # 3. If new content needed, create command file first
    if requires_new_command(change_description):
        suggest_new_command_file(change_description)
        return create_reference_to_new_command()
    
    # 4. Only direct update if absolutely minimal
    if is_micro_update(change_description):
        return create_minimal_inline_update()
    
    # 5. Default: suggest command creation
    return "Consider creating .claude/commands/[topic].md instead"
```

## Token Optimization Metrics

**Target Efficiency:**
- New content in CLAUDE.md: < 10 lines
- References to .claude/commands/: Unlimited
- Total token increase: < 100 tokens per update
- Duplication factor: 0% (no content duplication)

## Examples

### Example 1: Adding New Testing Rule
```markdown
# ❌ WRONG (500+ tokens):
### Advanced Testing Patterns
[Long detailed testing rules...]

# ✅ CORRECT (50 tokens):
### Advanced Testing Patterns
**Korean Test Standards**: @/.claude/commands/write-unit-test.md
**Performance Testing**: @/.claude/rules/performance-testing.md
```

### Example 2: Project Integration Update
```markdown
# ✅ MINIMAL UPDATE:
## ECS Architecture Testing
**Component Testing**: Follow ECS patterns in test design
**Reference**: @/.claude/commands/write-unit-test.md#ecs-patterns
```

This command ensures CLAUDE.md remains lean while providing comprehensive guidance through strategic referencing.