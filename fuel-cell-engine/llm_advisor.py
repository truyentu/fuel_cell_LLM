"""
LLM Advisor — Claude API integration for in-loop reasoning.
Called when engine encounters situations needing human-like judgment.
"""

import logging
from typing import Optional

logger = logging.getLogger("engine.llm")


class LLMAdvisor:
    """Call Claude API when engine needs reasoning (stuck, high failure, anomaly)."""

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", False)
        self.model = config.get("model", "claude-sonnet-4-20250514")
        self.max_calls = config.get("max_llm_calls", 5)
        self.base_url = config.get("base_url", None)  # e.g. "https://vip.claudible.io/v1"
        self.call_count = 0
        self.client = None

        if self.enabled:
            try:
                import anthropic
                import os
                kwargs = {}
                # Use base_url from config or env
                base_url = self.base_url or os.environ.get("ANTHROPIC_BASE_URL")
                if base_url:
                    kwargs["base_url"] = base_url
                    logger.info(f"LLM Advisor using gateway: {base_url}")
                self.client = anthropic.Anthropic(**kwargs)
                logger.info(f"LLM Advisor enabled: {self.model}, max {self.max_calls} calls")
            except (ImportError, Exception) as e:
                logger.warning(f"LLM Advisor disabled: {e}")
                self.enabled = False

    def ask(self, context: str, question: str) -> Optional[str]:
        """
        Ask Claude for advice. Returns response text or None.

        Args:
            context: Current pipeline state (scores, failures, bounds)
            question: Specific question for Claude

        Returns:
            Response text, or None if disabled/maxed/error
        """
        if not self.enabled or not self.client:
            logger.debug("LLM advisor disabled, skipping")
            return None

        if self.call_count >= self.max_calls:
            logger.warning(f"LLM max calls reached ({self.max_calls}), skipping")
            return None

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=(
                    "You are a materials science expert advising an automated "
                    "catalyst screening pipeline for PGM-free AEMFC (Ni@C anode). "
                    "Be concise. Output actionable parameters (numbers, ranges, "
                    "specific suggestions). No lengthy explanations."
                ),
                messages=[{
                    "role": "user",
                    "content": f"Pipeline context:\n{context}\n\nQuestion:\n{question}"
                }]
            )
            self.call_count += 1
            result = response.content[0].text
            logger.info(
                f"LLM call #{self.call_count}/{self.max_calls}: "
                f"Q='{question[:60]}...' → {len(result)} chars"
            )
            return result

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return None

    @property
    def calls_remaining(self) -> int:
        return max(0, self.max_calls - self.call_count)

    def should_trigger(self, trigger_type: str, triggers_config, **kwargs) -> bool:
        """Check if a trigger condition is met."""
        # Handle both dict and Pydantic model
        if isinstance(triggers_config, dict):
            trigger = triggers_config.get(trigger_type)
        else:
            trigger = getattr(triggers_config, trigger_type, None)

        if trigger is None or trigger is False:
            return False
        if trigger is True:
            return True

        # Extract value from trigger (dict or Pydantic object)
        def _get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        if trigger_type == "high_failure_rate":
            threshold = _get(trigger, "threshold", 0.3)
            return kwargs.get("failure_rate", 0) > threshold

        elif trigger_type == "convergence_stalled":
            n_no_improve = _get(trigger, "n_iter_no_improve", 5)
            return kwargs.get("n_no_improve", 0) >= n_no_improve

        elif trigger_type == "ensemble_disagreement":
            std_threshold = _get(trigger, "std_threshold", 0.15)
            return kwargs.get("max_std", 0) > std_threshold

        elif trigger_type == "anomaly_detected":
            return kwargs.get("anomaly", False)

        return False
