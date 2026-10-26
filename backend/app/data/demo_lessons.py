from app.models.learning import (
    AssessmentChoice,
    AssessmentQuestion,
    CodeSnippet,
    DiagramComponent,
    DiagramDescription,
    DiagramRelationship,
    LearningActivity,
    LearningTopic,
    Lesson,
    RealWorldExample,
    TeachingStep,
    VisualizationEvent,
)


PYTHON_TOPIC = LearningTopic(
    topic_id="python-for-loops",
    title="Understanding Python for loops",
    description="A demonstration of repeating an action across a sequence.",
    category="Programming and technology",
    difficulty="beginner",
    goal="Understand how a for loop visits each item in a sequence.",
    prerequisites=["Recognize a sequence of values"],
    estimated_duration_minutes=12,
)

ARCHITECTURE_TOPIC = LearningTopic(
    topic_id="web-application-architecture",
    title="Understanding a web application's architecture",
    description=(
        "A demonstration of how a browser, API, and database can work together."
    ),
    category="Programming and technology",
    difficulty="beginner",
    goal="Describe a basic request and response through an application.",
    estimated_duration_minutes=15,
)

META_TOPIC = LearningTopic(
    topic_id="meta-business-model",
    title="Understanding Meta's business model",
    description=(
        "A simplified educational illustration of users, products, and "
        "advertising as business-model concepts."
    ),
    category="Business and companies",
    difficulty="beginner",
    goal="Identify conceptual relationships in an illustrative business model.",
    estimated_duration_minutes=10,
)

PYTHON_LESSON = Lesson(
    lesson_id="python-for-loops",
    title="Understanding Python for loops",
    topic=PYTHON_TOPIC,
    objectives=[
        "Explain that a for loop processes each item in a sequence.",
        "Trace the loop variable and output for a short example.",
    ],
    estimated_duration_minutes=12,
    teaching_strategy="Concrete delivery-route analogy followed by code tracing",
    activities=["Trace the driver's next stop for each item in the route."],
    assessment_methods=["Multiple-choice knowledge check"],
    research_status="demonstration_only",
    message="Illustrative programming demonstration; no code is executed.",
    steps=[
        TeachingStep(
            step_id="loop-analogy",
            title="A delivery route",
            explanation=(
                "Imagine a driver visiting each house on a delivery list. "
                "The driver handles one stop, then moves to the next."
            ),
            key_concepts=["sequence", "repetition", "current item"],
            examples=[
                RealWorldExample(
                    title="Delivery driver",
                    description="Visit each listed house once, in order.",
                )
            ],
            visualization_events=[
                VisualizationEvent(
                    event_id="visit-first-house",
                    event_type="highlight",
                    target_ids=["house-1"],
                    parameters={"visit_number": 1},
                    narration="The driver begins at the first house.",
                    caption="Visit 1",
                    expected_state={"current_house": "house-1"},
                ),
                VisualizationEvent(
                    event_id="move-to-next-house",
                    event_type="move",
                    target_ids=["delivery-driver", "house-2"],
                    parameters={"direction": "forward"},
                    narration="After the delivery, the driver moves on.",
                    caption="Continue to the next stop",
                    expected_state={"current_house": "house-2"},
                ),
            ],
            activities=[
                LearningActivity(
                    activity_id="trace-route",
                    activity_type="simulation",
                    instructions="Select the next house the driver should visit.",
                    interactive=True,
                )
            ],
            knowledge_checks=[
                AssessmentQuestion(
                    assessment_id="route-next-stop",
                    question_type="multiple_choice",
                    prompt="What does the driver do after completing one stop?",
                    choices=[
                        AssessmentChoice(choice_id="repeat", text="Visit the next stop"),
                        AssessmentChoice(choice_id="finish", text="Skip every other stop"),
                    ],
                    hints=["Think about how the driver follows the list."],
                    max_attempts=2,
                )
            ],
        ),
        TeachingStep(
            step_id="loop-code-trace",
            title="Read the loop",
            explanation=(
                "The loop assigns one house to `house` at a time and prints "
                "a delivery message for each value."
            ),
            key_concepts=["for statement", "loop variable", "indented body"],
            code_snippets=[
                CodeSnippet(
                    language="python",
                    code=(
                        'houses = ["Oak St", "Pine St", "Maple St"]\n'
                        "for house in houses:\n"
                        '    print(f"Delivering to {house}")'
                    ),
                    expected_output=(
                        "Delivering to Oak St\n"
                        "Delivering to Pine St\n"
                        "Delivering to Maple St"
                    ),
                )
            ],
            visualization_events=[
                VisualizationEvent(
                    event_id="loop-iteration-oak",
                    event_type="highlight",
                    target_ids=["loop-line-2", "loop-variable-house"],
                    parameters={"iteration": 1},
                    code_line_numbers=[2, 3],
                    narration="On the first iteration, house is Oak St.",
                    caption="house = Oak St",
                    expected_state={"house": "Oak St"},
                ),
                VisualizationEvent(
                    event_id="loop-output-oak",
                    event_type="show_output",
                    target_ids=["output-line-1"],
                    parameters={"text": "Delivering to Oak St"},
                    narration="The loop body prints a message for this stop.",
                    caption="First delivery",
                    expected_state={"output_count": 1},
                ),
            ],
            highlighted_elements=["loop-variable-house", "loop-line-3"],
        ),
        TeachingStep(
            step_id="loop-check",
            title="Check the number of visits",
            explanation="Each list item is visited once in this example.",
            knowledge_checks=[
                AssessmentQuestion(
                    assessment_id="loop-visit-count",
                    question_type="short_answer",
                    prompt="How many delivery messages does this list produce?",
                    hints=["Count the items in the houses list."],
                    max_attempts=2,
                )
            ],
        ),
    ],
)

ARCHITECTURE_DIAGRAM = DiagramDescription(
    diagram_id="student-app-architecture",
    title="A student application request",
    description=(
        "An illustrative flow: a student's browser sends a request to an API, "
        "which may read or write data in a database."
    ),
    components=[
        DiagramComponent(
            component_id="student-browser",
            label="Student browser",
            component_type="client",
            description="Displays the application interface.",
        ),
        DiagramComponent(
            component_id="student-api",
            label="Application API",
            component_type="service",
            description="Validates requests and coordinates application work.",
        ),
        DiagramComponent(
            component_id="student-database",
            label="Application database",
            component_type="data_store",
            description="Stores application data.",
        ),
    ],
    relationships=[
        DiagramRelationship(
            source_component_id="student-browser",
            target_component_id="student-api",
            label="request and response",
        ),
        DiagramRelationship(
            source_component_id="student-api",
            target_component_id="student-database",
            label="read or write data",
        ),
    ],
)

ARCHITECTURE_LESSON = Lesson(
    lesson_id="web-application-architecture",
    title="Understanding a web application's architecture",
    topic=ARCHITECTURE_TOPIC,
    objectives=[
        "Identify a client, an API, and a data store in a simple diagram.",
        "Describe the direction of a request and response.",
    ],
    estimated_duration_minutes=15,
    teaching_strategy="Component diagram with a request-flow explanation",
    activities=["Trace a student's sign-in request through the diagram."],
    assessment_methods=["Short-answer explanation"],
    research_status="demonstration_only",
    message="Generic architecture illustration; not tied to a specific service.",
    steps=[
        TeachingStep(
            step_id="architecture-components",
            title="Meet the components",
            explanation=(
                "A browser presents the application. An API handles requests, "
                "and a database can store application information."
            ),
            diagrams=[ARCHITECTURE_DIAGRAM],
            visual_assets=[
                # Stable IDs let the frontend render this structured diagram.
                {
                    "asset_id": "student-app-architecture",
                    "asset_type": "diagram",
                    "description": "Student browser, API, and database flow.",
                }
            ],
            visualization_events=[
                VisualizationEvent(
                    event_id="request-reaches-api",
                    event_type="draw_connection",
                    target_ids=["student-browser", "student-api"],
                    parameters={"direction": "request"},
                    narration="The browser sends a request to the API.",
                    caption="Request",
                    expected_state={"request_at": "student-api"},
                ),
                VisualizationEvent(
                    event_id="api-reads-database",
                    event_type="draw_connection",
                    target_ids=["student-api", "student-database"],
                    parameters={"direction": "data_request"},
                    narration="The API may read the information it needs.",
                    caption="Data request",
                    expected_state={"active_component": "student-database"},
                ),
            ],
            knowledge_checks=[
                AssessmentQuestion(
                    assessment_id="architecture-client",
                    question_type="multiple_choice",
                    prompt="Which component presents the application to the student?",
                    choices=[
                        AssessmentChoice(
                            choice_id="browser",
                            text="The student's browser",
                        ),
                        AssessmentChoice(
                            choice_id="database",
                            text="The database",
                        ),
                    ],
                    hints=["Think about where the user sees the interface."],
                )
            ],
        ),
        TeachingStep(
            step_id="architecture-request-flow",
            title="Trace a request",
            explanation=(
                "For this generic example, the browser communicates with the "
                "API; the API may then interact with a data store."
            ),
            examples=[
                RealWorldExample(
                    title="Student application",
                    description=(
                        "A student requests a page; an API coordinates the "
                        "response and any needed data access."
                    ),
                )
            ],
        ),
    ],
)

META_LESSON = Lesson(
    lesson_id="meta-business-model",
    title="Understanding Meta's business model",
    topic=META_TOPIC,
    objectives=[
        "Distinguish a simplified business-model illustration from live research.",
        "Describe a conceptual relationship among users, products, and advertisers.",
    ],
    estimated_duration_minutes=10,
    teaching_strategy="Qualified concept map and reflective discussion",
    activities=[
        "Discuss what additional sources would be needed to verify current details."
    ],
    assessment_methods=["Reflective discussion"],
    research_status="not_researched",
    message=(
        "Educational illustration only. No live research was conducted, and "
        "this content does not state current financial or operational figures."
    ),
    steps=[
        TeachingStep(
            step_id="meta-concept-map",
            title="A simplified concept map",
            explanation=(
                "As a conceptual illustration, consider how a company may "
                "connect people using products with organizations seeking to "
                "reach audiences. This is not a complete or current account "
                "of Meta's business."
            ),
            key_concepts=[
                "products",
                "audiences",
                "advertising concept",
                "business model",
            ],
            diagrams=[
                DiagramDescription(
                    diagram_id="illustrative-meta-model",
                    title="Illustrative business-model concepts",
                    description=(
                        "A non-quantitative teaching diagram, not live-verified "
                        "company research."
                    ),
                    components=[
                        DiagramComponent(
                            component_id="people",
                            label="People using products",
                            component_type="audience",
                        ),
                        DiagramComponent(
                            component_id="digital-products",
                            label="Digital products",
                            component_type="product",
                        ),
                        DiagramComponent(
                            component_id="organizations",
                            label="Organizations",
                            component_type="customer_group",
                        ),
                    ],
                    relationships=[
                        DiagramRelationship(
                            source_component_id="people",
                            target_component_id="digital-products",
                            label="illustrative product use",
                        ),
                        DiagramRelationship(
                            source_component_id="organizations",
                            target_component_id="digital-products",
                            label="illustrative advertising concept",
                        ),
                    ],
                )
            ],
            visualization_events=[
                VisualizationEvent(
                    event_id="show-illustrative-relationship",
                    event_type="reveal",
                    target_ids=["people", "digital-products", "organizations"],
                    parameters={"illustrative_only": True},
                    narration=(
                        "This is a simplified conceptual diagram, not a "
                        "verified current business analysis."
                    ),
                    caption="Illustrative concepts, not live research",
                    expected_state={"research_status": "not_researched"},
                )
            ],
            activities=[
                LearningActivity(
                    activity_id="identify-evidence",
                    activity_type="reflection",
                    instructions=(
                        "Name one current company claim that would need a "
                        "reliable source before being presented as fact."
                    ),
                )
            ],
        )
    ],
)

DEMONSTRATION_LESSONS: dict[str, Lesson] = {
    lesson.lesson_id: lesson
    for lesson in (PYTHON_LESSON, ARCHITECTURE_LESSON, META_LESSON)
}

DEMONSTRATION_TOPICS = [
    PYTHON_TOPIC,
    ARCHITECTURE_TOPIC,
    META_TOPIC,
]
