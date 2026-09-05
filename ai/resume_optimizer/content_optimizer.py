# Project scaffold file
"""
content_optimizer.py

Resume content optimization engine for an AI Resume Screening System.

Features:
- Analyze resume content against a job description
- Identify missing keywords and skills
- Improve weak resume bullet points
- Suggest stronger action verbs
- Improve keyword placement
- Improve bullet-point structure
- Detect vague / weak language
- Generate ATS-friendly recommendations
- Preserve factual integrity by avoiding invented experience
- Produce an explainable optimization report

Designed to work with:
    ai.information_extraction.entity_extractor
    ai.scoring.skill_scorer
    ai.scoring.ats_scorer
    ai.resume_optimizer.keyword_optimizer
    ai.resume_optimizer.bullet_optimizer
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Set, Tuple


# ============================================================
# Data Models
# ============================================================

@dataclass
class ContentIssue:
    """
    Represents one content-quality issue.
    """

    category: str
    original_text: str
    suggestion: str
    priority: str
    reason: str


@dataclass
class OptimizedBullet:
    """
    Represents an optimized resume bullet.
    """

    original: str
    optimized: str
    changes: List[str]
    confidence: float


@dataclass
class ContentOptimizationResult:
    """
    Complete resume content optimization report.
    """

    overall_score: float

    keyword_score: float
    readability_score: float
    action_verb_score: float
    achievement_score: float
    structure_score: float

    matched_keywords: List[str]
    missing_keywords: List[str]

    weak_phrases: List[str]
    recommended_action_verbs: List[str]

    optimized_bullets: List[OptimizedBullet]
    issues: List[ContentIssue]

    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "overall_score": self.overall_score,
            "keyword_score": self.keyword_score,
            "readability_score": self.readability_score,
            "action_verb_score": self.action_verb_score,
            "achievement_score": self.achievement_score,
            "structure_score": self.structure_score,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "weak_phrases": self.weak_phrases,
            "recommended_action_verbs": self.recommended_action_verbs,
            "optimized_bullets": [
                asdict(item)
                for item in self.optimized_bullets
            ],
            "issues": [
                asdict(item)
                for item in self.issues
            ],
            "recommendations": self.recommendations,
        }


# ============================================================
# Content Optimizer
# ============================================================

class ContentOptimizer:
    """
    Explainable resume content optimization engine.

    Scoring:

        Keyword relevance   -> 30%
        Readability         -> 15%
        Action verbs        -> 15%
        Achievements        -> 20%
        Structure           -> 20%

    Final score: 0-100

    IMPORTANT:
        This optimizer does not invent skills, employers,
        metrics, projects, certifications, or experience.

        Suggested metrics should be filled only when the
        candidate can verify them.
    """

    WEIGHTS = {
        "keyword": 0.30,
        "readability": 0.15,
        "action_verb": 0.15,
        "achievement": 0.20,
        "structure": 0.20,
    }

    # ========================================================
    # Action Verbs
    # ========================================================

    STRONG_ACTION_VERBS = {
        "achieved",
        "analyzed",
        "architected",
        "automated",
        "built",
        "collaborated",
        "configured",
        "created",
        "deployed",
        "designed",
        "developed",
        "engineered",
        "implemented",
        "improved",
        "integrated",
        "launched",
        "led",
        "migrated",
        "optimized",
        "orchestrated",
        "reduced",
        "refactored",
        "resolved",
        "scaled",
        "streamlined",
        "tested",
        "transformed",
        "trained",
        "maintained",
        "delivered",
        "managed",
        "mentored",
        "evaluated",
        "researched",
        "processed",
        "automated",
        "monitored",
        "secured",
        "modernized",
    }

    WEAK_ACTION_VERBS = {
        "worked",
        "helped",
        "did",
        "made",
        "used",
        "handled",
        "responsible",
        "responsible for",
        "involved",
        "participated",
        "assisted",
        "supported",
        "dealt",
        "looked after",
        "worked on",
    }

    ACTION_VERB_REPLACEMENTS = {
        "worked on": "developed",
        "worked with": "collaborated with",
        "helped": "supported",
        "made": "developed",
        "did": "executed",
        "used": "leveraged",
        "handled": "managed",
        "responsible for": "managed",
        "involved in": "contributed to",
        "participated in": "contributed to",
        "assisted": "supported",
        "dealt with": "resolved",
        "looked after": "managed",
    }

    # ========================================================
    # Weak Phrases
    # ========================================================

    WEAK_PHRASES = {
        "hard worker",
        "hardworking",
        "team player",
        "good communication skills",
        "excellent communication skills",
        "quick learner",
        "fast learner",
        "self motivated",
        "self-motivated",
        "detail oriented",
        "detail-oriented",
        "results driven",
        "results-driven",
        "responsible for",
        "duties included",
        "worked on",
        "helped with",
        "involved in",
        "various tasks",
        "many tasks",
        "etc.",
        "and more",
        "as needed",
    }

    # ========================================================
    # Achievement Indicators
    # ========================================================

    ACHIEVEMENT_PATTERNS = [
        r"\b\d+(?:\.\d+)?\s*%",
        r"\b\d+(?:\.\d+)?\s*(?:percent|percentage)\b",
        r"\b\d+(?:\.\d+)?\s*(?:x|times)\b",
        r"\b\d+(?:\.\d+)?\s*(?:million|billion|thousand|k)\b",
        r"\b(?:reduced|increased|improved|saved|grew|boosted)"
        r"\b.{0,80}\b\d+",
        r"\b(?:from|to)\s+\d+",
        r"\b\d+\s+(?:users|customers|clients|projects|"
        r"applications|services|systems|records|requests)\b",
    ]

    # ========================================================
    # Common Resume Sections
    # ========================================================

    RESUME_SECTIONS = {
        "summary",
        "professional summary",
        "profile",
        "objective",
        "skills",
        "technical skills",
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "education",
        "projects",
        "certifications",
        "awards",
        "achievements",
        "publications",
    }

    # ========================================================
    # Initialization
    # ========================================================

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.weights = (
            weights or self.WEIGHTS.copy()
        )

        self._validate_weights()

    def _validate_weights(self) -> None:

        if abs(
            sum(self.weights.values()) - 1.0
        ) > 0.001:

            raise ValueError(
                "Content optimizer weights must sum to 1.0."
            )

    # ========================================================
    # Text Normalization
    # ========================================================

    @staticmethod
    def normalize(
        text: str,
    ) -> str:

        text = text.lower()

        text = text.replace(
            "–",
            "-",
        )

        text = text.replace(
            "—",
            "-",
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ========================================================
    # Sentence Extraction
    # ========================================================

    @staticmethod
    def split_sentences(
        text: str,
    ) -> List[str]:

        if not text:
            return []

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            line = re.sub(
                r"^[•●▪◦*-]\s*",
                "",
                line,
            )

            if line:
                lines.append(line)

        return lines

    # ========================================================
    # Keyword Extraction
    # ========================================================

    def extract_keywords(
        self,
        job_description: str,
    ) -> Set[str]:

        """
        Extract useful multi-word and technical keywords
        from a job description.

        This is intentionally conservative.
        """

        normalized = self.normalize(
            job_description
        )

        keywords = set()

        # Technical keyword vocabulary.
        technical_patterns = [
            r"\bpython\b",
            r"\bjava\b",
            r"\bjavascript\b",
            r"\btypescript\b",
            r"\bc\+\+\b",
            r"\bc#\b",
            r"\bsql\b",
            r"\bmysql\b",
            r"\bpostgresql\b",
            r"\bmongodb\b",
            r"\bredis\b",

            r"\breact(?:\.js)?\b",
            r"\bangular\b",
            r"\bvue(?:\.js)?\b",
            r"\bnode(?:\.js)?\b",

            r"\bdjango\b",
            r"\bflask\b",
            r"\bfastapi\b",
            r"\bspring boot\b",

            r"\bmachine learning\b",
            r"\bdeep learning\b",
            r"\bartificial intelligence\b",
            r"\bnatural language processing\b",
            r"\bnlp\b",
            r"\bcomputer vision\b",
            r"\bgenerative ai\b",
            r"\blarge language models?\b",
            r"\bllm\b",

            r"\btensorflow\b",
            r"\bpytorch\b",
            r"\bscikit-learn\b",

            r"\bdocker\b",
            r"\bkubernetes\b",
            r"\bterraform\b",

            r"\baws\b",
            r"\bazure\b",
            r"\bgcp\b",

            r"\bgit\b",
            r"\bgithub\b",

            r"\brest(?:ful)? api\b",
            r"\bgraphql\b",
            r"\bmicroservices?\b",

            r"\bci/cd\b",
            r"\bjenkins\b",

            r"\bpower bi\b",
            r"\btableau\b",
        ]

        for pattern in technical_patterns:

            for match in re.finditer(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            ):

                keywords.add(
                    match.group().lower()
                )

        # Important professional terms.
        professional_patterns = [
            r"\bdata analysis\b",
            r"\bdata engineering\b",
            r"\bsoftware development\b",
            r"\bsoftware engineering\b",
            r"\bapi development\b",
            r"\bcloud computing\b",
            r"\bcloud architecture\b",
            r"\bscalable systems?\b",
            r"\bdistributed systems?\b",
            r"\btest automation\b",
            r"\bproject management\b",
            r"\bagile\b",
            r"\bscrum\b",
            r"\bdevops\b",
        ]

        for pattern in professional_patterns:

            for match in re.finditer(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            ):

                keywords.add(
                    match.group().lower()
                )

        return keywords

    # ========================================================
    # Keyword Matching
    # ========================================================

    def calculate_keyword_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> Tuple[
        float,
        Set[str],
        Set[str],
    ]:

        required_keywords = self.extract_keywords(
            job_description
        )

        resume_normalized = self.normalize(
            resume_text
        )

        matched = set()
        missing = set()

        for keyword in required_keywords:

            if keyword in resume_normalized:

                matched.add(keyword)

            else:

                missing.add(keyword)

        if not required_keywords:
            return 100.0, matched, missing

        score = (
            len(matched) /
            len(required_keywords)
        ) * 100

        return (
            round(score, 2),
            matched,
            missing,
        )

    # ========================================================
    # Weak Phrase Detection
    # ========================================================

    def find_weak_phrases(
        self,
        resume_text: str,
    ) -> List[str]:

        normalized = self.normalize(
            resume_text
        )

        found = []

        for phrase in self.WEAK_PHRASES:

            if phrase in normalized:

                found.append(phrase)

        return sorted(found)

    # ========================================================
    # Action Verb Score
    # ========================================================

    def calculate_action_verb_score(
        self,
        resume_text: str,
    ) -> float:

        lines = self.split_sentences(
            resume_text
        )

        bullet_lines = [
            line
            for line in lines
            if self.looks_like_bullet(line)
        ]

        if not bullet_lines:
            bullet_lines = lines

        if not bullet_lines:
            return 0.0

        strong = 0

        for line in bullet_lines:

            first_word = (
                self.normalize(line)
                .split(" ")[0]
                if line
                else ""
            )

            if first_word in self.STRONG_ACTION_VERBS:

                strong += 1

        return round(
            strong /
            len(bullet_lines) *
            100,
            2,
        )

    # ========================================================
    # Bullet Detection
    # ========================================================

    @staticmethod
    def looks_like_bullet(
        line: str,
    ) -> bool:

        return bool(
            re.match(
                r"^\s*[•●▪◦*-]\s+",
                line,
            )
        )

    # ========================================================
    # Achievement Score
    # ========================================================

    def calculate_achievement_score(
        self,
        resume_text: str,
    ) -> float:

        lines = self.split_sentences(
            resume_text
        )

        if not lines:
            return 0.0

        achievement_lines = 0

        for line in lines:

            if self.contains_achievement(
                line
            ):
                achievement_lines += 1

        return round(
            achievement_lines /
            len(lines) *
            100,
            2,
        )

    def contains_achievement(
        self,
        text: str,
    ) -> bool:

        for pattern in self.ACHIEVEMENT_PATTERNS:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):
                return True

        return False

    # ========================================================
    # Readability Score
    # ========================================================

    def calculate_readability_score(
        self,
        resume_text: str,
    ) -> float:

        lines = self.split_sentences(
            resume_text
        )

        if not lines:
            return 0.0

        score = 100.0

        for line in lines:

            words = line.split()

            # Very long bullets are harder to scan.
            if len(words) > 45:
                score -= 5

            elif len(words) > 35:
                score -= 3

            # Extremely short content may be vague.
            if len(words) < 3:
                score -= 2

        # Excessive punctuation.
        punctuation_count = len(
            re.findall(
                r"[!]{2,}|[?]{2,}",
                resume_text,
            )
        )

        score -= punctuation_count * 2

        return round(
            max(
                0.0,
                min(100.0, score),
            ),
            2,
        )

    # ========================================================
    # Structure Score
    # ========================================================

    def calculate_structure_score(
        self,
        resume_text: str,
    ) -> float:

        normalized = self.normalize(
            resume_text
        )

        score = 0.0

        detected_sections = 0

        for section in self.RESUME_SECTIONS:

            if re.search(
                rf"\b{re.escape(section)}\b",
                normalized,
            ):

                detected_sections += 1

        # Up to 70 points for section organization.
        score += min(
            70,
            detected_sections * 10,
        )

        # Bullet usage.
        bullets = sum(
            1
            for line in resume_text.splitlines()
            if self.looks_like_bullet(line)
        )

        if bullets >= 5:
            score += 20

        elif bullets >= 3:
            score += 15

        elif bullets >= 1:
            score += 10

        # Contact information.
        if re.search(
            r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
            resume_text,
        ):
            score += 5

        # Excessively long raw paragraphs.
        paragraphs = [
            p.strip()
            for p in resume_text.split("\n\n")
            if p.strip()
        ]

        if paragraphs:

            long_paragraphs = sum(
                1
                for paragraph in paragraphs
                if len(paragraph.split()) > 120
            )

            if long_paragraphs == 0:
                score += 5

        return round(
            min(100.0, score),
            2,
        )

    # ========================================================
    # Recommended Action Verbs
    # ========================================================

    def recommend_action_verbs(
        self,
        resume_text: str,
    ) -> List[str]:

        weak = self.find_weak_phrases(
            resume_text
        )

        recommendations = []

        for phrase in weak:

            replacement = (
                self.ACTION_VERB_REPLACEMENTS.get(
                    phrase
                )
            )

            if replacement:
                recommendations.append(
                    replacement
                )

        defaults = [
            "developed",
            "implemented",
            "optimized",
            "automated",
            "designed",
        ]

        for verb in defaults:

            if verb not in recommendations:
                recommendations.append(verb)

        return recommendations[:10]

    # ========================================================
    # Bullet Optimization
    # ========================================================

    def optimize_bullet(
        self,
        bullet: str,
    ) -> OptimizedBullet:

        original = bullet.strip()

        if not original:
            return OptimizedBullet(
                original=original,
                optimized=original,
                changes=[],
                confidence=0.0,
            )

        optimized = original
        changes = []

        # Remove bullet marker temporarily.
        prefix = ""

        marker_match = re.match(
            r"^(\s*[•●▪◦*-]\s*)",
            optimized,
        )

        if marker_match:

            prefix = marker_match.group()
            optimized = optimized[
                marker_match.end():
            ]

        # Replace weak opening phrases.
        for weak, strong in sorted(
            self.ACTION_VERB_REPLACEMENTS.items(),
            key=lambda item: -len(item[0]),
        ):

            pattern = re.compile(
                rf"^{re.escape(weak)}\b",
                flags=re.IGNORECASE,
            )

            if pattern.search(optimized):

                optimized = pattern.sub(
                    strong,
                    optimized,
                    count=1,
                )

                changes.append(
                    f"Replaced weak phrase "
                    f"'{weak}' with '{strong}'."
                )

                break

        # Remove vague "responsible for".
        pattern = re.compile(
            r"^responsible for\s+",
            flags=re.IGNORECASE,
        )

        if pattern.search(optimized):

            optimized = pattern.sub(
                "",
                optimized,
                count=1,
            )

            changes.append(
                "Removed passive 'responsible for' wording."
            )

        # Add a stronger verb when no action verb exists.
        words = optimized.split()

        if words:

            first_word = (
                re.sub(
                    r"[^a-zA-Z-]",
                    "",
                    words[0],
                ).lower()
            )

            if (
                first_word not in
                self.STRONG_ACTION_VERBS
            ):

                if first_word in {
                    "experience",
                    "experience:",
                    "task",
                    "tasks",
                }:

                    optimized = (
                        "Delivered "
                        + " ".join(words)
                    )

                    changes.append(
                        "Added a stronger action-oriented opening."
                    )

        # Replace vague phrase.
        vague_replacements = {
            "worked on": "developed",
            "worked with": "collaborated with",
            "helped with": "supported",
            "involved in": "contributed to",
            "made": "developed",
            "used": "leveraged",
        }

        for weak, strong in vague_replacements.items():

            pattern = re.compile(
                rf"\b{re.escape(weak)}\b",
                flags=re.IGNORECASE,
            )

            if pattern.search(optimized):

                optimized = pattern.sub(
                    strong,
                    optimized,
                )

                changes.append(
                    f"Improved vague phrase "
                    f"'{weak}'."
                )

        # Normalize whitespace.
        optimized = re.sub(
            r"\s+",
            " ",
            optimized,
        ).strip()

        # Restore bullet marker.
        optimized = prefix + optimized

        # Suggest achievement evidence.
        if not self.contains_achievement(
            optimized
        ):

            changes.append(
                "Consider adding a verified measurable "
                "outcome, such as percentage improvement, "
                "time saved, cost reduction, scale, or users served."
            )

        confidence = (
            0.90
            if changes
            else 0.75
        )

        return OptimizedBullet(
            original=original,
            optimized=optimized,
            changes=changes,
            confidence=confidence,
        )

    # ========================================================
    # Optimize All Bullets
    # ========================================================

    def optimize_bullets(
        self,
        resume_text: str,
    ) -> List[OptimizedBullet]:

        lines = self.split_sentences(
            resume_text
        )

        bullets = [
            line
            for line in lines
            if self.looks_like_bullet(line)
        ]

        return [
            self.optimize_bullet(
                bullet
            )
            for bullet in bullets
        ]

    # ========================================================
    # Content Issues
    # ========================================================

    def detect_issues(
        self,
        resume_text: str,
        missing_keywords: Set[str],
        weak_phrases: List[str],
    ) -> List[ContentIssue]:

        issues = []

        # Missing keywords.
        if missing_keywords:

            keywords = ", ".join(
                sorted(missing_keywords)[:8]
            )

            issues.append(
                ContentIssue(
                    category="keywords",
                    original_text="",
                    suggestion=(
                        f"Add relevant keywords where truthful: "
                        f"{keywords}."
                    ),
                    priority="high",
                    reason=(
                        "These terms appear relevant to the target "
                        "job but were not detected in the resume."
                    ),
                )
            )

        # Weak phrases.
        for phrase in weak_phrases:

            replacement = (
                self.ACTION_VERB_REPLACEMENTS.get(
                    phrase
                )
            )

            suggestion = (
                f"Replace '{phrase}'"
            )

            if replacement:
                suggestion += (
                    f" with '{replacement}'."
                )

            else:
                suggestion += (
                    " with specific evidence or an achievement."
                )

            issues.append(
                ContentIssue(
                    category="wording",
                    original_text=phrase,
                    suggestion=suggestion,
                    priority="medium",
                    reason=(
                        "The phrase is generic and provides "
                        "limited evidence of impact."
                    ),
                )
            )

        # Long bullets.
        for line in self.split_sentences(
            resume_text
        ):

            if len(line.split()) > 45:

                issues.append(
                    ContentIssue(
                        category="readability",
                        original_text=line,
                        suggestion=(
                            "Shorten this bullet and focus on "
                            "action, technology, and measurable outcome."
                        ),
                        priority="medium",
                        reason=(
                            "Long bullets are harder for recruiters "
                            "and ATS users to scan."
                        ),
                    )
                )

        # Missing achievements.
        achievement_score = (
            self.calculate_achievement_score(
                resume_text
            )
        )

        if achievement_score < 20:

            issues.append(
                ContentIssue(
                    category="achievements",
                    original_text="",
                    suggestion=(
                        "Add verified measurable outcomes to "
                        "key experience bullets."
                    ),
                    priority="high",
                    reason=(
                        "The resume contains few explicit "
                        "achievement indicators."
                    ),
                )
            )

        return issues

    # ========================================================
    # Recommendations
    # ========================================================

    def generate_recommendations(
        self,
        keyword_score: float,
        readability_score: float,
        action_verb_score: float,
        achievement_score: float,
        structure_score: float,
        missing_keywords: Set[str],
    ) -> List[str]:

        recommendations = []

        if keyword_score < 70:

            recommendations.append(
                "Tailor the resume to the target job by "
                "naturally including relevant missing keywords "
                "that accurately describe your experience."
            )

        if action_verb_score < 60:

            recommendations.append(
                "Start experience bullets with strong action "
                "verbs such as developed, implemented, optimized, "
                "automated, designed, or deployed."
            )

        if achievement_score < 50:

            recommendations.append(
                "Strengthen experience bullets with verified "
                "results, metrics, scale, or business impact."
            )

        if readability_score < 80:

            recommendations.append(
                "Shorten long bullets and remove unnecessary "
                "words to improve recruiter readability."
            )

        if structure_score < 80:

            recommendations.append(
                "Use clear sections and concise bullet points "
                "for easier ATS and recruiter scanning."
            )

        if missing_keywords:

            recommendations.append(
                "Do not add a keyword merely to improve an ATS "
                "score; include it only when it accurately "
                "represents your skills or experience."
            )

        if not recommendations:

            recommendations.append(
                "Resume content is well aligned. Focus on "
                "specific achievements and tailoring each "
                "application to the target role."
            )

        return recommendations

    # ========================================================
    # Main Optimization
    # ========================================================

    def optimize(
        self,
        resume_text: str,
        job_description: str,
    ) -> ContentOptimizationResult:

        if not resume_text.strip():

            raise ValueError(
                "Resume text cannot be empty."
            )

        if not job_description.strip():

            raise ValueError(
                "Job description cannot be empty."
            )

        # Keyword analysis.
        (
            keyword_score,
            matched_keywords,
            missing_keywords,
        ) = self.calculate_keyword_score(
            resume_text,
            job_description,
        )

        # Content-quality metrics.
        readability_score = (
            self.calculate_readability_score(
                resume_text
            )
        )

        action_verb_score = (
            self.calculate_action_verb_score(
                resume_text
            )
        )

        achievement_score = (
            self.calculate_achievement_score(
                resume_text
            )
        )

        structure_score = (
            self.calculate_structure_score(
                resume_text
            )
        )

        # Overall score.
        overall_score = (
            keyword_score *
            self.weights["keyword"]
            +
            readability_score *
            self.weights["readability"]
            +
            action_verb_score *
            self.weights["action_verb"]
            +
            achievement_score *
            self.weights["achievement"]
            +
            structure_score *
            self.weights["structure"]
        )

        weak_phrases = (
            self.find_weak_phrases(
                resume_text
            )
        )

        recommended_action_verbs = (
            self.recommend_action_verbs(
                resume_text
            )
        )

        optimized_bullets = (
            self.optimize_bullets(
                resume_text
            )
        )

        issues = self.detect_issues(
            resume_text=resume_text,
            missing_keywords=missing_keywords,
            weak_phrases=weak_phrases,
        )

        recommendations = (
            self.generate_recommendations(
                keyword_score=keyword_score,
                readability_score=readability_score,
                action_verb_score=action_verb_score,
                achievement_score=achievement_score,
                structure_score=structure_score,
                missing_keywords=missing_keywords,
            )
        )

        return ContentOptimizationResult(
            overall_score=round(
                overall_score,
                2,
            ),

            keyword_score=keyword_score,
            readability_score=readability_score,
            action_verb_score=action_verb_score,
            achievement_score=achievement_score,
            structure_score=structure_score,

            matched_keywords=sorted(
                matched_keywords
            ),

            missing_keywords=sorted(
                missing_keywords
            ),

            weak_phrases=weak_phrases,

            recommended_action_verbs=(
                recommended_action_verbs
            ),

            optimized_bullets=(
                optimized_bullets
            ),

            issues=issues,

            recommendations=recommendations,
        )


# ============================================================
# Helper Function
# ============================================================

def optimize_resume_content(
    resume_text: str,
    job_description: str,
) -> Dict:

    optimizer = ContentOptimizer()

    result = optimizer.optimize(
        resume_text=resume_text,
        job_description=job_description,
    )

    return result.to_dict()


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    resume = """
    JOHN DOE

    Professional Summary
    Hardworking software developer with good
    communication skills and experience in Python.

    Skills
    Python, FastAPI, SQL, PostgreSQL, Docker,
    AWS, Machine Learning, Git.

    Experience

    Software Engineer
    ABC Technologies

    - Worked on Python backend applications.
    - Responsible for developing REST APIs using FastAPI.
    - Helped with deployment using Docker and AWS.
    - Worked with SQL and PostgreSQL databases.
    - Participated in machine learning projects.

    Education
    B.Tech in Computer Science
    """

    job_description = """
    Machine Learning Engineer

    Requirements:
    Python
    Machine Learning
    FastAPI
    SQL
    PostgreSQL
    Docker
    AWS
    REST API

    Preferred:
    PyTorch
    Kubernetes
    Generative AI

    The candidate should be able to design scalable
    backend systems and automate deployments.
    """

    optimizer = ContentOptimizer()

    result = optimizer.optimize(
        resume_text=resume,
        job_description=job_description,
    )

    print("=" * 70)
    print("RESUME CONTENT OPTIMIZATION")
    print("=" * 70)

    print(
        f"\nOverall Score       : "
        f"{result.overall_score}%"
    )

    print(
        f"Keyword Score      : "
        f"{result.keyword_score}%"
    )

    print(
        f"Readability Score  : "
        f"{result.readability_score}%"
    )

    print(
        f"Action Verb Score  : "
        f"{result.action_verb_score}%"
    )

    print(
        f"Achievement Score  : "
        f"{result.achievement_score}%"
    )

    print(
        f"Structure Score     : "
        f"{result.structure_score}%"
    )

    print("\nMatched Keywords:")

    for keyword in result.matched_keywords:
        print(f"  ✓ {keyword}")

    print("\nMissing Keywords:")

    for keyword in result.missing_keywords:
        print(f"  ✗ {keyword}")

    print("\nWeak Phrases:")

    for phrase in result.weak_phrases:
        print(f"  ⚠ {phrase}")

    print("\nRecommended Action Verbs:")

    for verb in result.recommended_action_verbs:
        print(f"  → {verb}")

    print("\nOptimized Bullets:")

    for bullet in result.optimized_bullets:

        print("\nOriginal:")
        print(f"  {bullet.original}")

        print("Optimized:")
        print(f"  {bullet.optimized}")

        if bullet.changes:

            print("Changes:")

            for change in bullet.changes:
                print(f"  • {change}")

    print("\nIssues:")

    for issue in result.issues:

        print(
            f"\n[{issue.priority.upper()}] "
            f"{issue.category}"
        )

        if issue.original_text:
            print(
                f"Original: {issue.original_text}"
            )

        print(
            f"Suggestion: {issue.suggestion}"
        )

        print(
            f"Reason: {issue.reason}"
        )

    print("\nRecommendations:")

    for recommendation in result.recommendations:
        print(f"  → {recommendation}")