---
version: "1.0.0"
description: "Core global instruction set for all agents"
priority: 10
applicability: ["claude", "openai", "gemini"]
precedence: "override"
scope: "global"
deprecated: false
tags: ["core", "behavioral", "global"]
author: "system"
---

# Global Core Instructions

## Purpose
This document defines the foundational rules that all agents must follow without exception.

## Core Rules

### Rule 1: Version Checking
Always check versions first before proceeding with implementation. Never assume versions are correct.

### Rule 2: Test Naming
Use meaningful test names following the pattern: `givenXxx_whenYyy_thenZzz()`.

## Provider-Specific Behavior

<!-- if: provider=claude -->
Claude-specific instructions: Use comprehensive reasoning and multi-step thinking.
<!-- endif -->

<!-- if: provider=openai -->
OpenAI-specific instructions: Follow OpenAI API documentation strictly.
<!-- endif -->

<!-- if: provider=gemini -->
Gemini-specific instructions: Use Gemini Safety Settings appropriately.
<!-- endif -->

## Metadata Markers
<!-- meta: validation_required = true -->
<!-- meta: auto_update = false -->

This instruction set is critical for all operations.
