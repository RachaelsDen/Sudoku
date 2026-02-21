# generator_base.py
#
# Copyright 2025 sepehr-rs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
import logging
import multiprocessing as mp
import time
from typing import Any


logger = logging.getLogger(__name__)


class GeneratorBase(ABC):
    """Abstract puzzle generator with optional multiprocessing."""

    def generate(self, difficulty: float, timeout: int = 5):
        """
        Run the variant's `_generate_impl` in a subprocess with timeout.
        Returns (puzzle, solution).
        """
        start_time = time.time()
        logger.info(
            "Starting puzzle generation difficulty=%s timeout=%s",
            difficulty,
            timeout,
        )

        queue = mp.Queue()
        process = mp.Process(target=self._generate_worker, args=(queue, difficulty))
        process.start()
        process.join(timeout)

        if process.is_alive():
            logger.warning(
                "Puzzle generation timed out difficulty=%s timeout=%s",
                difficulty,
                timeout,
            )
            process.terminate()
            process.join()
            raise TimeoutError("Puzzle generation timed out")

        if not queue.empty():
            puzzle_solution = queue.get()
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(
                "Puzzle generated successfully difficulty=%s timeout=%s duration_ms=%s",
                difficulty,
                timeout,
                duration_ms,
            )
            return puzzle_solution

        logger.error(
            "Puzzle generation failed difficulty=%s timeout=%s exitcode=%s is_alive=%s",
            difficulty,
            timeout,
            process.exitcode,
            process.is_alive(),
        )
        raise RuntimeError("Failed to generate puzzle")

    def _generate_worker(self, queue: Any, difficulty: float) -> None:
        puzzle, solution = self._generate_impl(difficulty)
        queue.put((puzzle, solution))

    @abstractmethod
    def _generate_impl(
        self, difficulty: float
    ) -> tuple[list[list[int]], list[list[int]]]:
        """
        Must be implemented by variants.
        Return (puzzle, solution) as 2D lists.
        """
        pass
