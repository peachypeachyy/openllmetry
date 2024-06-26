import json

import pytest
from langchain.chains import SequentialChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from opentelemetry.semconv.ai import SpanAttributes


@pytest.mark.vcr
def test_sequential_chain(exporter):
    llm = OpenAI(temperature=0.7)
    synopsis_template = """You are a playwright. Given the title of play and the era it is set in, it is your job to write a synopsis for that title.

    Title: {title}
    Era: {era}
    Playwright: This is a synopsis for the above play:"""  # noqa: E501
    synopsis_prompt_template = PromptTemplate(
        input_variables=["title", "era"], template=synopsis_template
    )
    synopsis_chain = LLMChain(
        llm=llm, prompt=synopsis_prompt_template, output_key="synopsis"
    )

    template = """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.

    Play Synopsis:
    {synopsis}
    Review from a New York Times play critic of the above play:"""  # noqa: E501
    prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
    review_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="review")

    overall_chain = SequentialChain(
        chains=[synopsis_chain, review_chain],
        input_variables=["era", "title"],
        # Here we return multiple variables
        output_variables=["synopsis", "review"],
        verbose=True,
    )
    overall_chain(
        {"title": "Tragedy at sunset on the beach", "era": "Victorian England"}
    )

    spans = exporter.get_finished_spans()

    assert [
        "openai.completion",
        "LLMChain.langchain.task",
        "openai.completion",
        "LLMChain.langchain.task",
        "SequentialChain.langchain.workflow",
    ] == [span.name for span in spans]

    synopsis_span, review_span = [span for span in spans if span.name == "LLMChain.langchain.task"]

    data = json.loads(synopsis_span.attributes[SpanAttributes.TRACELOOP_ENTITY_INPUT])
    assert data["inputs"] == {'title': 'Tragedy at sunset on the beach', 'era': 'Victorian England'}
    assert data["kwargs"]["name"] == "LLMChain"
    data = json.loads(synopsis_span.attributes[SpanAttributes.TRACELOOP_ENTITY_OUTPUT])
    assert data["outputs"].keys() == {"synopsis", }

    data = json.loads(review_span.attributes[SpanAttributes.TRACELOOP_ENTITY_INPUT])
    assert data["inputs"].keys() == {"title", "era", "synopsis"}
    assert data["kwargs"]["name"] == "LLMChain"
    data = json.loads(review_span.attributes[SpanAttributes.TRACELOOP_ENTITY_OUTPUT])
    assert data["outputs"].keys() == {"review", }

    overall_span = next(span for span in spans if span.name == "SequentialChain.langchain.workflow")
    data = json.loads(overall_span.attributes[SpanAttributes.TRACELOOP_ENTITY_INPUT])
    assert data["inputs"] == {'title': 'Tragedy at sunset on the beach', 'era': 'Victorian England'}
    assert data["kwargs"]["name"] == "SequentialChain"
    data = json.loads(overall_span.attributes[SpanAttributes.TRACELOOP_ENTITY_OUTPUT])
    assert data["outputs"].keys() == {"synopsis", "review"}


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_asequential_chain(exporter):
    llm = OpenAI(temperature=0.7)
    synopsis_template = """You are a playwright. Given the title of play and the era it is set in, it is your job to write a synopsis for that title.

    Title: {title}
    Era: {era}
    Playwright: This is a synopsis for the above play:"""  # noqa: E501
    synopsis_prompt_template = PromptTemplate(
        input_variables=["title", "era"], template=synopsis_template
    )
    synopsis_chain = LLMChain(
        llm=llm, prompt=synopsis_prompt_template, output_key="synopsis"
    )

    template = """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.

    Play Synopsis:
    {synopsis}
    Review from a New York Times play critic of the above play:"""  # noqa: E501
    prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
    review_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="review")

    overall_chain = SequentialChain(
        chains=[synopsis_chain, review_chain],
        input_variables=["era", "title"],
        # Here we return multiple variables
        output_variables=["synopsis", "review"],
        verbose=True,
    )
    await overall_chain.ainvoke(
        {"title": "Tragedy at sunset on the beach", "era": "Victorian England"}
    )

    spans = exporter.get_finished_spans()

    assert [
        "openai.completion",
        "LLMChain.langchain.task",
        "openai.completion",
        "LLMChain.langchain.task",
        "SequentialChain.langchain.workflow",
    ] == [span.name for span in spans]

    synopsis_span, review_span = [span for span in spans if span.name == "LLMChain.langchain.task"]

    data = json.loads(synopsis_span.attributes[SpanAttributes.TRACELOOP_ENTITY_INPUT])
    assert data["inputs"] == {'title': 'Tragedy at sunset on the beach', 'era': 'Victorian England'}
    assert data["kwargs"]["name"] == "LLMChain"
    data = json.loads(synopsis_span.attributes[SpanAttributes.TRACELOOP_ENTITY_OUTPUT])
    assert data["outputs"].keys() == {"synopsis", }

    data = json.loads(review_span.attributes[SpanAttributes.TRACELOOP_ENTITY_INPUT])
    assert data["inputs"].keys() == {"title", "era", "synopsis"}
    assert data["kwargs"]["name"] == "LLMChain"
    data = json.loads(review_span.attributes[SpanAttributes.TRACELOOP_ENTITY_OUTPUT])
    assert data["outputs"].keys() == {"review", }

    overall_span = next(span for span in spans if span.name == "SequentialChain.langchain.workflow")
    data = json.loads(overall_span.attributes[SpanAttributes.TRACELOOP_ENTITY_INPUT])
    assert data["inputs"] == {'title': 'Tragedy at sunset on the beach', 'era': 'Victorian England'}
    assert data["kwargs"]["name"] == "SequentialChain"
    data = json.loads(overall_span.attributes[SpanAttributes.TRACELOOP_ENTITY_OUTPUT])
    assert data["outputs"].keys() == {"synopsis", "review"}
