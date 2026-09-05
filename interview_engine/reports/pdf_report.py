"""
Interview PDF Report Generator.

Converts interview reports and scorecards into PDF documents.

Responsibilities:
- Generate professional interview PDF reports
- Display overall interview score
- Display category-wise scores
- Display strengths and improvement areas
- Display question-level evaluation
- Display recommendations
- Support both dataclass objects and dictionaries
- Save PDF reports to disk
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class PDFReportError(Exception):
    """Base exception for PDF report generation."""


class InvalidPDFReportInputError(
    PDFReportError
):
    """Raised when report data is invalid."""


# ----------------------------------------------------------------------
# PDF Generator
# ----------------------------------------------------------------------


class InterviewPDFReportGenerator:
    """
    Generate a PDF interview report.

    Example:

        generator = InterviewPDFReportGenerator()

        path = generator.generate(
            report,
            "storage/interview_reports/report.pdf"
        )
    """

    def __init__(
        self,
        page_size=A4,
        margin: float = 18 * mm,
    ) -> None:

        self.page_size = page_size
        self.margin = margin

        self.styles = (
            self._create_styles()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        report: Any,
        output_path: str | Path,
        recommendations: Optional[Any] = None,
        title: str = "Interview Evaluation Report",
    ) -> Path:
        """
        Generate an interview PDF.

        Args:
            report:
                InterviewReport object or dictionary.

            output_path:
                Destination PDF path.

            recommendations:
                Optional InterviewRecommendations object.

            title:
                PDF title.

        Returns:
            Path to generated PDF.
        """

        report_data = self._normalize(
            report
        )

        recommendation_data = (
            self._normalize(
                recommendations
            )
            if recommendations is not None
            else None
        )

        output = Path(
            output_path
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = SimpleDocTemplate(
            str(output),
            pagesize=self.page_size,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=title,
            author="AI Resume Screening & Interview System",
        )

        story = []

        # --------------------------------------------------------------
        # Header
        # --------------------------------------------------------------

        story.extend(
            self._build_header(
                title
            )
        )

        # --------------------------------------------------------------
        # Candidate / Interview Metadata
        # --------------------------------------------------------------

        story.extend(
            self._build_metadata_section(
                report_data
            )
        )

        # --------------------------------------------------------------
        # Overall Score
        # --------------------------------------------------------------

        story.extend(
            self._build_overall_score_section(
                report_data
            )
        )

        # --------------------------------------------------------------
        # Category Scores
        # --------------------------------------------------------------

        story.extend(
            self._build_category_section(
                report_data
            )
        )

        # --------------------------------------------------------------
        # Summary
        # --------------------------------------------------------------

        story.extend(
            self._build_summary_section(
                report_data
            )
        )

        # --------------------------------------------------------------
        # Strengths
        # --------------------------------------------------------------

        story.extend(
            self._build_bullet_section(
                "Key Strengths",
                report_data.get(
                    "strengths",
                    [],
                ),
            )
        )

        # --------------------------------------------------------------
        # Improvements
        # --------------------------------------------------------------

        story.extend(
            self._build_bullet_section(
                "Areas for Improvement",
                report_data.get(
                    "improvement_areas",
                    [],
                ),
            )
        )

        # --------------------------------------------------------------
        # Category Summaries
        # --------------------------------------------------------------

        story.extend(
            self._build_category_summaries(
                report_data
            )
        )

        # --------------------------------------------------------------
        # Recommendations
        # --------------------------------------------------------------

        if recommendation_data:
            story.extend(
                self._build_recommendations_section(
                    recommendation_data
                )
            )

        # --------------------------------------------------------------
        # Question-Level Results
        # --------------------------------------------------------------

        story.append(
            PageBreak()
        )

        story.extend(
            self._build_question_section(
                report_data
            )
        )

        # --------------------------------------------------------------
        # Disclaimer
        # --------------------------------------------------------------

        story.extend(
            self._build_disclaimer()
        )

        document.build(
            story,
            onFirstPage=self._footer,
            onLaterPages=self._footer,
        )

        logger.info(
            "Interview PDF report generated: %s",
            output,
        )

        return output

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(
        self,
        title: str,
    ) -> List[Any]:

        return [
            Paragraph(
                self._escape(title),
                self.styles[
                    "ReportTitle"
                ],
            ),
            Spacer(
                1,
                4 * mm,
            ),
            HRFlowable(
                width="100%",
                thickness=1,
                spaceBefore=1 * mm,
                spaceAfter=5 * mm,
            ),
        ]

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def _build_metadata_section(
        self,
        report: Mapping[str, Any],
    ) -> List[Any]:

        metadata = dict(
            report.get(
                "metadata",
                {},
            )
            or {}
        )

        rows = []

        candidate_name = metadata.get(
            "candidate_name"
        )

        job_title = metadata.get(
            "job_title"
        )

        interview_id = report.get(
            "interview_id"
        )

        generated_at = report.get(
            "generated_at"
        )

        if candidate_name:
            rows.append(
                [
                    "Candidate",
                    str(candidate_name),
                ]
            )

        if job_title:
            rows.append(
                [
                    "Position",
                    str(job_title),
                ]
            )

        if interview_id:
            rows.append(
                [
                    "Interview ID",
                    str(interview_id),
                ]
            )

        if generated_at:
            rows.append(
                [
                    "Generated",
                    self._format_datetime(
                        generated_at
                    ),
                ]
            )

        if not rows:
            return []

        table = Table(
            rows,
            colWidths=[
                40 * mm,
                125 * mm,
            ],
            hAlign="LEFT",
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (1, 0),
                        (1, -1),
                        "Helvetica",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        return [
            Paragraph(
                "Interview Information",
                self.styles[
                    "SectionTitle"
                ],
            ),
            table,
            Spacer(
                1,
                5 * mm,
            ),
        ]

    # ------------------------------------------------------------------
    # Overall Score
    # ------------------------------------------------------------------

    def _build_overall_score_section(
        self,
        report: Mapping[str, Any],
    ) -> List[Any]:

        score = self._number(
            report.get(
                "overall_score",
                0,
            )
        )

        level = str(
            report.get(
                "performance_level",
                "not_available",
            )
        ).replace(
            "_",
            " ",
        ).title()

        recommendation = str(
            report.get(
                "recommendation",
                "Not available",
            )
        ).replace(
            "_",
            " ",
        ).title()

        data = [
            [
                Paragraph(
                    "Overall Score",
                    self.styles[
                        "CardLabel"
                    ],
                ),
                Paragraph(
                    "Performance",
                    self.styles[
                        "CardLabel"
                    ],
                ),
                Paragraph(
                    "Assessment",
                    self.styles[
                        "CardLabel"
                    ],
                ),
            ],
            [
                Paragraph(
                    f"<b>{score:.1f}/100</b>",
                    self.styles[
                        "CardScore"
                    ],
                ),
                Paragraph(
                    level,
                    self.styles[
                        "CardValue"
                    ],
                ),
                Paragraph(
                    recommendation,
                    self.styles[
                        "CardValue"
                    ],
                ),
            ],
        ]

        table = Table(
            data,
            colWidths=[
                52 * mm,
                52 * mm,
                61 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        colors.grey,
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.lightgrey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.whitesmoke,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        return [
            Paragraph(
                "Overall Performance",
                self.styles[
                    "SectionTitle"
                ],
            ),
            table,
            Spacer(
                1,
                6 * mm,
            ),
        ]

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def _build_category_section(
        self,
        report: Mapping[str, Any],
    ) -> List[Any]:

        categories = (
            report.get(
                "category_scores",
                report.get(
                    "categories",
                    [],
                ),
            )
        )

        rows = [
            [
                "Category",
                "Score",
                "Weight",
                "Questions",
            ]
        ]

        for category in categories:

            category = self._normalize(
                category
            )

            name = str(
                category.get(
                    "name",
                    "Unknown",
                )
            ).title()

            score = self._number(
                category.get(
                    "score",
                    0,
                )
            )

            weight = self._number(
                category.get(
                    "weight",
                    0,
                )
            )

            if weight <= 1:
                weight_display = (
                    f"{weight * 100:.0f}%"
                )
            else:
                weight_display = (
                    f"{weight:.0f}%"
                )

            question_count = category.get(
                "question_count",
                0,
            )

            rows.append(
                [
                    name,
                    f"{score:.1f}/100",
                    weight_display,
                    str(
                        question_count
                    ),
                ]
            )

        if len(rows) == 1:
            return []

        table = Table(
            rows,
            colWidths=[
                60 * mm,
                35 * mm,
                35 * mm,
                35 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#EDEDED"
                        ),
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        return [
            Paragraph(
                "Category Scores",
                self.styles[
                    "SectionTitle"
                ],
            ),
            table,
            Spacer(
                1,
                6 * mm,
            ),
        ]

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def _build_summary_section(
        self,
        report: Mapping[str, Any],
    ) -> List[Any]:

        summary = str(
            report.get(
                "summary",
                "",
            )
        ).strip()

        recruiter_summary = str(
            report.get(
                "recruiter_summary",
                "",
            )
        ).strip()

        candidate_feedback = str(
            report.get(
                "candidate_feedback",
                "",
            )
        ).strip()

        elements = [
            Paragraph(
                "Interview Summary",
                self.styles[
                    "SectionTitle"
                ],
            )
        ]

        if summary:
            elements.append(
                Paragraph(
                    self._escape(
                        summary
                    ),
                    self.styles[
                        "Body"
                    ],
                )
            )

        if recruiter_summary:
            elements.extend(
                [
                    Spacer(
                        1,
                        3 * mm,
                    ),
                    Paragraph(
                        "<b>Recruiter Summary</b>",
                        self.styles[
                            "Body"
                        ],
                    ),
                    Paragraph(
                        self._escape(
                            recruiter_summary
                        ),
                        self.styles[
                            "Body"
                        ],
                    ),
                ]
            )

        if candidate_feedback:
            elements.extend(
                [
                    Spacer(
                        1,
                        3 * mm,
                    ),
                    Paragraph(
                        "<b>Candidate Feedback</b>",
                        self.styles[
                            "Body"
                        ],
                    ),
                    Paragraph(
                        self._escape(
                            candidate_feedback
                        ),
                        self.styles[
                            "Body"
                        ],
                    ),
                ]
            )

        elements.append(
            Spacer(
                1,
                5 * mm,
            )
        )

        return elements

    # ------------------------------------------------------------------
    # Bullet Sections
    # ------------------------------------------------------------------

    def _build_bullet_section(
        self,
        title: str,
        items: Sequence[Any],
    ) -> List[Any]:

        normalized = [
            str(item).strip()
            for item in items
            if str(item).strip()
        ]

        if not normalized:
            return []

        elements = [
            Paragraph(
                self._escape(title),
                self.styles[
                    "SectionTitle"
                ],
            )
        ]

        for item in normalized:
            elements.append(
                Paragraph(
                    f"• {self._escape(item)}",
                    self.styles[
                        "Bullet"
                    ],
                )
            )

        elements.append(
            Spacer(
                1,
                4 * mm,
            )
        )

        return elements

    # ------------------------------------------------------------------
    # Category Summaries
    # ------------------------------------------------------------------

    def _build_category_summaries(
        self,
        report: Mapping[str, Any],
    ) -> List[Any]:

        summaries = [
            (
                "Technical Performance",
                report.get(
                    "technical_summary",
                    "",
                ),
            ),
            (
                "Communication Performance",
                report.get(
                    "communication_summary",
                    "",
                ),
            ),
            (
                "Confidence Performance",
                report.get(
                    "confidence_summary",
                    "",
                ),
            ),
        ]

        elements = [
            Paragraph(
                "Performance Analysis",
                self.styles[
                    "SectionTitle"
                ],
            )
        ]

        has_content = False

        for title, summary in summaries:

            summary = str(
                summary
            ).strip()

            if not summary:
                continue

            has_content = True

            elements.extend(
                [
                    Paragraph(
                        self._escape(
                            title
                        ),
                        self.styles[
                            "SubTitle"
                        ],
                    ),
                    Paragraph(
                        self._escape(
                            summary
                        ),
                        self.styles[
                            "Body"
                        ],
                    ),
                    Spacer(
                        1,
                        2 * mm,
                    ),
                ]
            )

        if not has_content:
            return []

        elements.append(
            Spacer(
                1,
                4 * mm,
            )
        )

        return elements

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def _build_recommendations_section(
        self,
        recommendations: Mapping[
            str,
            Any,
        ],
    ) -> List[Any]:

        elements = [
            Paragraph(
                "Recommendations",
                self.styles[
                    "SectionTitle"
                ],
            )
        ]

        status = recommendations.get(
            "recommendation_status"
        )

        recruiter = recommendations.get(
            "recruiter_recommendation"
        )

        if status:
            elements.append(
                Paragraph(
                    "<b>Status:</b> "
                    + self._escape(
                        str(status).replace(
                            "_",
                            " ",
                        ).title()
                    ),
                    self.styles[
                        "Body"
                    ],
                )
            )

        if recruiter:
            elements.extend(
                [
                    Spacer(
                        1,
                        2 * mm,
                    ),
                    Paragraph(
                        self._escape(
                            str(
                                recruiter
                            )
                        ),
                        self.styles[
                            "Body"
                        ],
                    ),
                ]
            )

        items = recommendations.get(
            "recommendations",
            [],
        )

        for item in items:

            item = self._normalize(
                item
            )

            title = str(
                item.get(
                    "title",
                    "Recommendation",
                )
            )

            priority = str(
                item.get(
                    "priority",
                    "medium",
                )
            ).title()

            description = str(
                item.get(
                    "description",
                    "",
                )
            )

            action = str(
                item.get(
                    "action",
                    "",
                )
            )

            block = [
                Paragraph(
                    self._escape(
                        f"{title} — {priority} Priority"
                    ),
                    self.styles[
                        "SubTitle"
                    ],
                )
            ]

            if description:
                block.append(
                    Paragraph(
                        self._escape(
                            description
                        ),
                        self.styles[
                            "Body"
                        ],
                    )
                )

            if action:
                block.append(
                    Paragraph(
                        "<b>Suggested Action:</b> "
                        + self._escape(
                            action
                        ),
                        self.styles[
                            "Body"
                        ],
                    )
                )

            block.append(
                Spacer(
                    1,
                    3 * mm,
                )
            )

            elements.append(
                KeepTogether(
                    block
                )
            )

        follow_up = recommendations.get(
            "follow_up_actions",
            [],
        )

        if follow_up:
            elements.append(
                Paragraph(
                    "Suggested Follow-up",
                    self.styles[
                        "SubTitle"
                    ],
                )
            )

            for action in follow_up:
                elements.append(
                    Paragraph(
                        "• "
                        + self._escape(
                            str(action)
                        ),
                        self.styles[
                            "Bullet"
                        ],
                    )
                )

        elements.append(
            Spacer(
                1,
                5 * mm,
            )
        )

        return elements

    # ------------------------------------------------------------------
    # Question Results
    # ------------------------------------------------------------------

    def _build_question_section(
        self,
        report: Mapping[str, Any],
    ) -> List[Any]:

        questions = report.get(
            "question_reports",
            report.get(
                "questions",
                [],
            ),
        )

        if not questions:
            return [
                Paragraph(
                    "Question-Level Evaluation",
                    self.styles[
                        "SectionTitle"
                    ],
                ),
                Paragraph(
                    "No question-level results are available.",
                    self.styles[
                        "Body"
                    ],
                ),
            ]

        elements = [
            Paragraph(
                "Question-Level Evaluation",
                self.styles[
                    "SectionTitle"
                ],
            )
        ]

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question = self._normalize(
                question
            )

            question_text = str(
                question.get(
                    "question",
                    f"Question {index}",
                )
            )

            question_id = str(
                question.get(
                    "question_id",
                    index,
                )
            )

            score = self._number(
                question.get(
                    "overall_score",
                    0,
                )
            )

            technical = question.get(
                "technical_score"
            )

            communication = question.get(
                "communication_score"
            )

            confidence = question.get(
                "confidence_score"
            )

            answer = str(
                question.get(
                    "answer",
                    "",
                )
            )

            strengths = question.get(
                "strengths",
                [],
            )

            improvements = question.get(
                "improvement_areas",
                question.get(
                    "improvements",
                    [],
                ),
            )

            heading = (
                f"{index}. "
                f"{question_text}"
            )

            elements.append(
                Paragraph(
                    self._escape(
                        heading
                    ),
                    self.styles[
                        "QuestionTitle"
                    ],
                )
            )

            score_rows = [
                [
                    "Overall",
                    f"{score:.1f}",
                    "Technical",
                    self._format_optional_score(
                        technical
                    ),
                    "Communication",
                    self._format_optional_score(
                        communication
                    ),
                    "Confidence",
                    self._format_optional_score(
                        confidence
                    ),
                ]
            ]

            table = Table(
                score_rows,
                colWidths=[
                    17 * mm,
                    14 * mm,
                    20 * mm,
                    14 * mm,
                    25 * mm,
                    17 * mm,
                    20 * mm,
                    17 * mm,
                ],
            )

            table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.grey,
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            7.5,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, -1),
                            "Helvetica",
                        ),
                        (
                            "ALIGN",
                            (1, 0),
                            (-1, -1),
                            "CENTER",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE",
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            4,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            4,
                        ),
                    ]
                )
            )

            elements.append(
                table
            )

            if answer:
                elements.extend(
                    [
                        Paragraph(
                            "<b>Answer</b>",
                            self.styles[
                                "SmallHeading"
                            ],
                        ),
                        Paragraph(
                            self._escape(
                                answer
                            ),
                            self.styles[
                                "SmallBody"
                            ],
                        ),
                    ]
                )

            if strengths:
                elements.append(
                    Paragraph(
                        "<b>Strengths</b>",
                        self.styles[
                            "SmallHeading"
                        ],
                    )
                )

                for strength in strengths:
                    elements.append(
                        Paragraph(
                            "• "
                            + self._escape(
                                str(
                                    strength
                                )
                            ),
                            self.styles[
                                "SmallBody"
                            ],
                        )
                    )

            if improvements:
                elements.append(
                    Paragraph(
                        "<b>Improvements</b>",
                        self.styles[
                            "SmallHeading"
                        ],
                    )
                )

                for improvement in improvements:
                    elements.append(
                        Paragraph(
                            "• "
                            + self._escape(
                                str(
                                    improvement
                                )
                            ),
                            self.styles[
                                "SmallBody"
                            ],
                        )
                    )

            elements.append(
                Spacer(
                    1,
                    6 * mm,
                )
            )

        return elements

    # ------------------------------------------------------------------
    # Disclaimer
    # ------------------------------------------------------------------

    def _build_disclaimer(
        self,
    ) -> List[Any]:

        return [
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.grey,
                spaceBefore=5 * mm,
                spaceAfter=3 * mm,
            ),
            Paragraph(
                (
                    "<b>Important:</b> This report summarizes "
                    "interview evaluation signals and should be "
                    "used as decision-support information. It is "
                    "not a standalone automated hiring decision. "
                    "Recruiters should review the underlying "
                    "evidence, job requirements, and applicable "
                    "fairness and employment policies."
                ),
                self.styles[
                    "Disclaimer"
                ],
            ),
        ]

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def _create_styles(self):

        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=20,
                leading=24,
                alignment=TA_CENTER,
                spaceAfter=4 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SectionTitle",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=16,
                alignment=TA_LEFT,
                spaceBefore=4 * mm,
                spaceAfter=3 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SubTitle",
                parent=styles["Heading3"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                spaceBefore=2 * mm,
                spaceAfter=1.5 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="Body",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                spaceAfter=2 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="Bullet",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                leftIndent=5 * mm,
                firstLineIndent=-3 * mm,
                spaceAfter=1.5 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="CardLabel",
                parent=styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=8,
                alignment=TA_CENTER,
            )
        )

        styles.add(
            ParagraphStyle(
                name="CardScore",
                parent=styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=17,
                alignment=TA_CENTER,
            )
        )

        styles.add(
            ParagraphStyle(
                name="CardValue",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                alignment=TA_CENTER,
                leading=12,
            )
        )

        styles.add(
            ParagraphStyle(
                name="QuestionTitle",
                parent=styles["Heading3"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                spaceBefore=2 * mm,
                spaceAfter=2 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SmallHeading",
                parent=styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=11,
                spaceBefore=2 * mm,
                spaceAfter=1 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SmallBody",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=8,
                leading=11,
                spaceAfter=1 * mm,
            )
        )

        styles.add(
            ParagraphStyle(
                name="Disclaimer",
                parent=styles["BodyText"],
                fontName="Helvetica-Oblique",
                fontSize=7,
                leading=10,
                textColor=colors.grey,
            )
        )

        return styles

    # ------------------------------------------------------------------
    # Page Footer
    # ------------------------------------------------------------------

    def _footer(
        self,
        canvas,
        document,
    ) -> None:

        canvas.saveState()

        width, _ = self.page_size

        canvas.setFont(
            "Helvetica",
            7,
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.drawString(
            self.margin,
            10 * mm,
            "AI Resume Screening & Interview System",
        )

        canvas.drawRightString(
            width - self.margin,
            10 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(
        value: Any,
    ) -> Dict[str, Any]:
        """Convert supported objects into dictionaries."""

        if value is None:
            return {}

        if isinstance(
            value,
            Mapping,
        ):
            return dict(
                value
            )

        if hasattr(
            value,
            "to_dict",
        ):
            result = value.to_dict()

            if isinstance(
                result,
                Mapping,
            ):
                return dict(
                    result
                )

        if hasattr(
            value,
            "__dict__",
        ):
            return dict(
                vars(value)
            )

        raise InvalidPDFReportInputError(
            "Unsupported report object."
        )

    @staticmethod
    def _number(
        value: Any,
    ) -> float:
        """Convert value to a number."""

        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _format_optional_score(
        value: Any,
    ) -> str:

        if value is None:
            return "N/A"

        try:
            return f"{float(value):.1f}"
        except (
            TypeError,
            ValueError,
        ):
            return "N/A"

    @staticmethod
    def _format_datetime(
        value: Any,
    ) -> str:

        if not value:
            return ""

        try:
            parsed = datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    "+00:00",
                )
            )

            return parsed.strftime(
                "%d %b %Y, %H:%M UTC"
            )

        except (
            ValueError,
            TypeError,
        ):
            return str(
                value
            )

    @staticmethod
    def _escape(
        value: str,
    ) -> str:
        """
        Escape XML-sensitive characters for ReportLab Paragraph.
        """

        value = str(
            value
        )

        return (
            value.replace(
                "&",
                "&amp;",
            )
            .replace(
                "<",
                "&lt;",
            )
            .replace(
                ">",
                "&gt;",
            )
        )


# ----------------------------------------------------------------------
# Convenience Functions
# ----------------------------------------------------------------------


def generate_pdf_report(
    report: Any,
    output_path: str | Path,
    recommendations: Optional[Any] = None,
) -> Path:
    """
    Generate a PDF report using the default generator.
    """

    generator = (
        InterviewPDFReportGenerator()
    )

    return generator.generate(
        report=report,
        output_path=output_path,
        recommendations=recommendations,
    )


def generate_report_pdf(
    report: Any,
    output_path: str | Path,
    recommendations: Optional[Any] = None,
) -> Path:
    """
    Backwards-compatible alias for generate_pdf_report().
    """

    return generate_pdf_report(
        report=report,
        output_path=output_path,
        recommendations=recommendations,
    )


__all__ = [
    "InterviewPDFReportGenerator",
    "PDFReportError",
    "InvalidPDFReportInputError",
    "generate_pdf_report",
    "generate_report_pdf",
]