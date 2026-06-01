"""Orchestrator: Master coordinator for 11-agent pipeline.

Loads configurations, initializes ExecutionContext, and orchestrates the
14-step pipeline including maturity iteration and report generation.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from context_builder.config.loader import ConfigLoader
from context_builder.models import (
    ExecutionContext,
    Graph,
    WorkspaceConfig,
    ProjectConfig,
    TechAliases,
    ScanConfig,
    MaturityConfig,
    TestQualityConfig,
    Report,
)
from context_builder.agents.base_agent import BaseAgent, AgentRegistry
from context_builder.agents.project_definition_agent import ProjectDefinitionAgent
from context_builder.agents.repo_scanner_agent import RepoScannerAgent
from context_builder.agents.code_graph_agent import CodeGraphAgent
from context_builder.agents.flow_analysis_agent import FlowAnalysisAgent
from context_builder.agents.c4_diagram_agent import C4DiagramAgent
from context_builder.agents.html_site_agent import HTMLSiteAgent
from context_builder.agents.rag_agent import RAGAgent
from context_builder.agents.test_intelligence_agent import TestIntelligenceAgent
from context_builder.agents.technical_debt_agent import TechnicalDebtAgent
from context_builder.agents.maturity_agent import MaturityAgent


class Orchestrator:
    """Master coordinator orchestrating 11 sub-agents in 14-step pipeline.

    Responsibilities:
    - Load configs via ConfigLoader
    - Initialize ExecutionContext
    - Execute agents in sequence (STEP 1-11)
    - Check maturity gate (STEP 12)
    - Iterate if maturity < target
    - Generate reports (STEP 13-14)
    - Export agent definitions to .context/agents/

    Attributes:
        context_root: Path to .context directory
        config_loader: ConfigLoader instance for loading configs
        context: ExecutionContext for orchestration state
        agents: List of agents to execute in sequence
        max_iterations: Maximum maturity refinement iterations
        target_maturity: Target maturity score (0-100)
        logger: Logger instance
    """

    def __init__(self, context_root: Path):
        """Initialize Orchestrator.

        Args:
            context_root: Path to .context directory (or parent project root)
        """
        # Handle case where user passes project root instead of .context
        context_root = Path(context_root)
        if context_root.name != ".context" and (context_root / ".context").exists():
            context_root = context_root / ".context"

        self.context_root = context_root
        self.config_loader = ConfigLoader(context_root)
        self.context: Optional[ExecutionContext] = None
        self.agents: list[BaseAgent] = []
        self.agent_registry = AgentRegistry()
        self.max_iterations = 5
        self.target_maturity = 80
        self.logger = logging.getLogger(__name__)

        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_configs(self) -> Dict[str, Any]:
        """Load all configuration files.

        Returns:
            Dictionary with keys: workspace, project, tech_aliases, scan,
            maturity, test_quality
        """
        self.logger.info("Loading configurations from %s", self.context_root)
        all_configs = self.config_loader.load_all_configs()

        workspace_cfg = all_configs.get("workspace", {})
        project_cfg = all_configs.get("project", {})
        tech_aliases_cfg = all_configs.get("tech_aliases", {})
        scan_cfg = all_configs.get("scan", {})
        maturity_cfg = all_configs.get("maturity", {})
        test_quality_cfg = all_configs.get("test_quality", {})

        self.logger.info("Loaded workspace config: %s", workspace_cfg.get("name", "N/A"))
        self.logger.info("Loaded %d project(s)", len(project_cfg.get("projects", [])))

        return {
            "workspace": workspace_cfg,
            "project": project_cfg,
            "tech_aliases": tech_aliases_cfg,
            "scan": scan_cfg,
            "maturity": maturity_cfg,
            "test_quality": test_quality_cfg,
        }

    def _initialize_context(self, configs: Dict[str, Any]) -> ExecutionContext:
        """Initialize ExecutionContext from loaded configs.

        Args:
            configs: Dictionary with all loaded configurations

        Returns:
            Initialized ExecutionContext
        """
        self.logger.info("Initializing ExecutionContext")

        workspace_config = None
        if configs["workspace"]:
            workspace_config = WorkspaceConfig(
                id=configs["workspace"].get("id", "default"),
                name=configs["workspace"].get("name", "Workspace"),
                description=configs["workspace"].get("description", ""),
                context_root=self.context_root,
                repositories=configs["workspace"].get("repositories", []),
                gitlab_enabled=configs["workspace"].get("gitlab_enabled", False),
                gitlab_base_url=configs["workspace"].get("gitlab_base_url"),
                gitlab_group=configs["workspace"].get("gitlab_group"),
            )

        project_config = None
        if configs["project"]:
            project_config = ProjectConfig(
                projects=configs["project"].get("projects", [])
            )

        tech_aliases = None
        if configs["tech_aliases"]:
            tech_aliases = TechAliases(
                aliases=configs["tech_aliases"].get("aliases", [])
            )

        scan_config = ScanConfig(
            include_patterns=configs["scan"].get("include", []),
            exclude_patterns=configs["scan"].get("exclude", []),
            analysis_depth=configs["scan"].get("analysis_depth", {}),
            incremental=configs["scan"].get("incremental", True),
        )

        maturity_config = MaturityConfig(
            target_score=configs["maturity"].get("target_score", 80),
            max_iterations=configs["maturity"].get("max_iterations", 5),
            dimensions=configs["maturity"].get("dimensions", {}),
        )
        self.target_maturity = maturity_config.target_score
        self.max_iterations = maturity_config.max_iterations

        test_quality_config = TestQualityConfig(
            target_score=configs["test_quality"].get("target_score", 80),
            coverage_sources=configs["test_quality"].get("coverage_sources", {}),
            scoring=configs["test_quality"].get("scoring", {}),
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=project_config,
            tech_aliases=tech_aliases,
            scan_config=scan_config,
            maturity_config=maturity_config,
            test_quality_config=test_quality_config,
            graph=Graph(),
            reports={},
            iteration=0,
            generated_files=[],
            logger=self.logger,
        )

        self.logger.info("ExecutionContext initialized with maturity target: %d", self.target_maturity)
        return context

    def _register_agents(self) -> None:
        """Register all 11 sub-agents in execution order.

        Agents execute in sequence:
        1. ProjectDefinitionAgent
        2. RepoScannerAgent
        3. CodeGraphAgent
        4. FlowAnalysisAgent
        5. C4DiagramAgent
        6. HTMLSiteAgent
        7. RAGAgent
        8. TestIntelligenceAgent
        9. TechnicalDebtAgent
        10. MaturityAgent
        """
        agents = [
            ProjectDefinitionAgent(),
            RepoScannerAgent(),
            CodeGraphAgent(),
            FlowAnalysisAgent(),
            C4DiagramAgent(),
            HTMLSiteAgent(),
            RAGAgent(),
            TestIntelligenceAgent(),
            TechnicalDebtAgent(),
            MaturityAgent(),
        ]

        for agent in agents:
            self.agent_registry.register(agent)
            self.agents.append(agent)

        self.logger.info("Registered %d agents", len(self.agents))

    def _execute_agents(self, from_step: int = 1) -> bool:
        """Execute all registered agents in sequence.

        Args:
            from_step: Starting agent step (1-indexed). Used for iteration.
                      Default 1 starts from ProjectDefinitionAgent.
                      Value 4 starts from FlowAnalysisAgent.

        Returns:
            True if all agents succeed, False if any critical error occurred
        """
        # from_step is 1-indexed, but agents list is 0-indexed
        start_index = from_step - 1
        executing_agents = self.agents[start_index:]

        for i, agent in enumerate(executing_agents):
            step_number = from_step + i
            self.logger.info("[STEP %d] Executing %s", step_number, agent.name)

            try:
                output = agent.execute(self.context)

                if output.status == "success":
                    self.logger.info("[STEP %d] %s completed successfully", step_number, agent.name)

                    # Store artifacts and metrics
                    if output.artifacts:
                        self.context.generated_files.extend(output.artifacts)

                    # Store report if generated
                    if output.message:
                        self.context.reports[agent.name.lower()] = Report(
                            name=agent.name,
                            content=output.message,
                            metrics=output.metrics,
                        )
                else:
                    self.logger.error(
                        "[STEP %d] %s failed: %s",
                        step_number,
                        agent.name,
                        output.message,
                    )

                    if output.errors:
                        for error in output.errors:
                            self.logger.error("  - %s", error)

                    # Critical errors halt orchestration
                    if agent.name in ["ProjectDefinitionAgent", "RepoScannerAgent"]:
                        self.logger.error("Critical agent failed. Halting orchestration.")
                        return False

                    # Non-critical warnings logged and continue
                    self.logger.warning("Non-critical agent failed. Continuing orchestration.")

            except Exception as e:
                self.logger.error(
                    "[STEP %d] Exception in %s: %s",
                    step_number,
                    agent.name,
                    str(e),
                    exc_info=True,
                )

                if agent.name in ["ProjectDefinitionAgent", "RepoScannerAgent"]:
                    return False

        return True

    def _check_maturity_gate(self) -> bool:
        """Check if context maturity meets target.

        Returns:
            True if maturity >= target, False otherwise
        """
        maturity_report = self.context.reports.get("maturityagent")
        if not maturity_report:
            self.logger.warning("Maturity report not found. Using default score.")
            return False

        maturity_score = maturity_report.metrics.get("overall_score", 0)
        self.logger.info(
            "[MATURITY GATE] Current: %d/100, Target: %d/100",
            maturity_score,
            self.target_maturity,
        )

        return maturity_score >= self.target_maturity

    def build_context(self, until_mature: bool = False) -> bool:
        """Build complete project context with optional maturity iteration.

        Steps:
        1. Load configurations
        2. Initialize ExecutionContext
        3. Register agents
        4-13. Execute agents and check maturity gate
        14. Generate final reports and agent definitions

        Args:
            until_mature: If True, iterate until maturity >= target (max 5 iterations)

        Returns:
            True if build succeeded, False otherwise
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("Starting Context Build (until_mature=%s)", until_mature)
            self.logger.info("=" * 70)

            # STEP 0: Load and initialize
            configs = self._load_configs()
            self.context = self._initialize_context(configs)
            self._register_agents()

            self.logger.info("[STEP 0] Initialization complete")

            # Get max iterations from context config if available
            max_iterations = self.context.maturity_config.max_iterations if self.context.maturity_config else self.max_iterations

            # STEP 1-10: Execute agents with iteration
            for iteration in range(1, max_iterations + 1):
                self.context.iteration = iteration
                self.logger.info(
                    "[ITERATION %d/%d] Starting agent execution",
                    iteration,
                    max_iterations,
                )

                # On first iteration, start from STEP 1. On retries, start from STEP 4.
                from_step = 1 if iteration == 1 else 4
                success = self._execute_agents(from_step=from_step)

                if not success:
                    self.logger.error("Agent execution failed. Aborting.")
                    return False

                # STEP 12: Maturity gate check
                if until_mature:
                    maturity_met = self._check_maturity_gate()
                    if maturity_met:
                        self.logger.info(
                            "[MATURITY GATE] PASSED after iteration %d", iteration
                        )
                        break
                    elif iteration < max_iterations:
                        self.logger.info(
                            "[MATURITY GATE] FAILED. Re-running from STEP 4 (iteration %d/%d)",
                            iteration + 1,
                            max_iterations,
                        )
                        continue
                    else:
                        self.logger.warning(
                            "[MATURITY GATE] FAILED. Reached max iterations. "
                            "Generating final report with current maturity."
                        )

            # STEP 13-14: Generate final reports
            self.logger.info("[STEP 13-14] Generating final reports and agent definitions")
            self._generate_final_report()

            self.logger.info("=" * 70)
            self.logger.info("Context build COMPLETE")
            self.logger.info("=" * 70)

            return True

        except Exception as e:
            self.logger.error("Fatal error during context build: %s", str(e), exc_info=True)
            return False

    def _generate_final_report(self) -> None:
        """Generate final report and export agent definitions.

        Creates:
        - final_report.md with summary
        - Exports agents to .context/agents/
        """
        agents_dir = self.context_root / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        # Collect summary from all reports
        summary_lines = [
            "# Final Context Build Report\n",
            f"Iterations: {self.context.iteration}\n",
            f"Generated files: {len(self.context.generated_files)}\n",
            f"Reports: {len(self.context.reports)}\n",
            "\n## Report Summary\n",
        ]

        for report_name, report in self.context.reports.items():
            summary_lines.append(f"\n### {report_name}\n")
            summary_lines.append(f"{report.content[:200]}...\n")

        final_report_path = self.context_root / "final_report.md"
        final_report_path.write_text("".join(summary_lines))

        self.logger.info("Generated final report at %s", final_report_path)
        self.context.generated_files.append(final_report_path)

    def get_context(self) -> Optional[ExecutionContext]:
        """Get the ExecutionContext after build.

        Returns:
            ExecutionContext if build completed, None otherwise
        """
        return self.context

    def get_generated_files(self) -> list[Path]:
        """Get list of all generated files.

        Returns:
            List of Path objects for generated files
        """
        return self.context.generated_files if self.context else []

    def get_maturity_score(self) -> int:
        """Get current maturity score.

        Returns:
            Maturity score (0-100) or 0 if not available
        """
        if not self.context:
            return 0

        maturity_report = self.context.reports.get("maturityagent")
        if maturity_report:
            return maturity_report.metrics.get("overall_score", 0)

        return 0
