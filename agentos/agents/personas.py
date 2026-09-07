"""Personas and branch assignments for the org-chart agents.

One generic display name per agent (shown in Mattermost alongside the role
title) and a branch assignment per agent (drives which branch channel its
messages are mirrored to). Both are keyed by agent_id so they apply to the
seeded registry without re-seeding.
"""

from __future__ import annotations

# agent_id -> generic first name
PERSONAS: dict[str, str] = {
    # executive office
    "executive": "Alex",
    "chief-of-staff": "Jamie",
    # product
    "product-director": "Sam",
    "product-manager": "Riley",
    "requirements-analyst": "Quinn",
    "product-researcher": "Avery",
    # engineering
    "cto": "Jordan",
    "software-architect": "Casey",
    "frontend-lead": "Morgan",
    "backend-lead": "Taylor",
    "database-engineer": "Reese",
    "devops-engineer": "Rowan",
    "ai-engineer": "Skyler",
    # design
    "design-director": "Dakota",
    "ux-designer": "Emerson",
    "ui-designer": "Finley",
    "motion-engineer": "Harper",
    # research
    "research-director": "Jules",
    "market-researcher": "Kai",
    "community-researcher": "Logan",
    "competitor-analyst": "Micah",
    "technical-researcher": "Nico",
    # marketing
    "marketing-director": "Ollie",
    "seo-agent": "Parker",
    "content-agent": "Sage",
    "social-agent": "Theo",
    "growth-agent": "Val",
    # sales
    "sales-director": "Wren",
    "lead-researcher": "Zephyr",
    "sales-analyst": "Blake",
    "outreach-specialist": "Drew",
    # QA & security
    "qa-director": "Ellis",
    "test-engineer": "Frankie",
    "code-reviewer": "Gray",
    "security-reviewer": "Hollis",
    "performance-reviewer": "Indigo",
    # operations
    "operations-director": "Kit",
    "project-manager": "Lane",
    "documentation-agent": "Marlow",
    "deployment-agent": "Nori",
    "monitoring-agent": "Onyx",
}

# agent_id -> Mattermost username. Format: <persona>.<role-slug>, truncated to
# Mattermost's 22-char username limit (falls back to the bare persona).
USERNAMES: dict[str, str] = {
    aid: (f"{PERSONAS[aid].lower()}.{aid}" if len(f"{PERSONAS[aid].lower()}.{aid}") <= 22
          else PERSONAS[aid].lower())
    for aid in PERSONAS
}
USERNAMES["executive"] = "alex.ceo"  # executive-director is clearer as the CEO

# agent_id -> branch key
BRANCH_OF: dict[str, str] = {
    "executive": "executive", "chief-of-staff": "executive",
    "product-director": "product", "product-manager": "product",
    "requirements-analyst": "product", "product-researcher": "product",
    "cto": "engineering", "software-architect": "engineering",
    "frontend-lead": "engineering", "backend-lead": "engineering",
    "database-engineer": "engineering", "devops-engineer": "engineering",
    "ai-engineer": "engineering",
    "design-director": "design", "ux-designer": "design",
    "ui-designer": "design", "motion-engineer": "design",
    "research-director": "research", "market-researcher": "research",
    "community-researcher": "research", "competitor-analyst": "research",
    "technical-researcher": "research",
    "marketing-director": "marketing", "seo-agent": "marketing",
    "content-agent": "marketing", "social-agent": "marketing",
    "growth-agent": "marketing",
    "sales-director": "sales", "lead-researcher": "sales",
    "sales-analyst": "sales", "outreach-specialist": "sales",
    "qa-director": "qa", "test-engineer": "qa", "code-reviewer": "qa",
    "security-reviewer": "qa", "performance-reviewer": "qa",
    "operations-director": "operations", "project-manager": "operations",
    "documentation-agent": "operations", "deployment-agent": "operations",
    "monitoring-agent": "operations",
}

# branch key -> Mattermost channel name
BRANCH_CHANNELS: dict[str, str] = {
    key: f"branch-{key}" for key in sorted(set(BRANCH_OF.values()))
}


def branch_for(agent_id: str) -> str:
    return BRANCH_OF.get(agent_id, "operations")


def branch_channel_for(agent_id: str) -> str:
    return BRANCH_CHANNELS[branch_for(agent_id)]


def username_for(agent_id: str) -> str:
    return USERNAMES.get(agent_id, agent_id)


def token_for_agent(agent_id: str) -> str:
    """Personal access token for the agent's Mattermost account, injected via
    AGENT_TOKEN_<AGENT_ID> environment variables (agent-tokens.env)."""
    import os

    return os.environ.get(f"AGENT_TOKEN_{agent_id.upper().replace('-', '_')}", "")
