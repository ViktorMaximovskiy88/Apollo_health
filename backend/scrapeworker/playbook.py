from enum import Enum
from typing import Any, AsyncGenerator, Callable, Coroutine

from playwright.async_api import Page, TimeoutError

from backend.common.models.base_document import BaseModel


class PlaybookAction(Enum):
    CLICK = "click"
    SELECT = "select"
    WAIT_FOR_NAV = "wait"


class PlaybookStep(BaseModel):
    action: PlaybookAction
    target: str = ""
    choice: str = ""
    continue_steps: bool = False


PlaybookContext = list[PlaybookStep]


class ScrapePlaybook:
    playbook: list[PlaybookStep] = []

    def __init__(
        self, playbook_str: str | None, playbook_context: list[PlaybookStep] | None = None
    ) -> None:
        if playbook_context:
            self.playbook = playbook_context
        else:
            self.playbook = self.process_playbook_str(playbook_str)

    def process_playbook_str(self, playbook_str: str | None) -> list[PlaybookStep]:
        steps: list[PlaybookStep] = []
        if not playbook_str:
            return steps

        ignore_keywords = [
            "pupeteer.launch",
            "require('puppeteer')",
            "chromium.launch",
            "browser.close",
            "browser.newPage",
            "page.goto",
            "page.setViewport",
        ]
        for step_block in playbook_str.split("\n\n"):
            if any(i in step_block for i in ignore_keywords):
                continue  # skip setup code

            lines = step_block.split("\n")
            if step_block.startswith("continue"):
                steps[-1].continue_steps = True
                continue
            if step_block.startswith("await navigationPromise"):
                step = PlaybookStep(action=PlaybookAction.WAIT_FOR_NAV)
                steps.append(step)
                continue
            elif step_block.startswith("await page.selectOption"):
                _, target, _, choice, _ = lines[0].split("'")
                step = PlaybookStep(action=PlaybookAction.SELECT, target=target, choice=choice)
                steps.append(step)
                continue
            elif len(lines) == 2:
                is_wait_for = lines[0].startswith("await page.waitFor")
                is_click = lines[1].startswith("await page.click")
                if is_wait_for and is_click:
                    _, target, _ = lines[1].split("'")
                    step = PlaybookStep(action=PlaybookAction.CLICK, target=target)
                    steps.append(step)
                    continue

            raise Exception(f"Unknown Playbook Action: {step_block}")

        return steps

    async def next_step(
        self,
        page: Page,
        step: PlaybookStep,
        remaining_steps: list[PlaybookStep],
        new_context: PlaybookContext,
    ):
        if not step.continue_steps:
            yield page, new_context
        async for page, result_context in self.playbook_step(page, remaining_steps, new_context):
            yield page, result_context

    async def execute_step(
        self,
        page: Page,
        step: PlaybookStep,
        remaining_steps: list[PlaybookStep],
        new_context: PlaybookContext,
        action: Callable[..., Coroutine[Any, Any, None]],
    ):
        retries = 0
        await action(timeout=15000)
        try:
            async for page, context in self.next_step(page, step, remaining_steps, new_context):
                yield page, context
        except TimeoutError as err:
            if retries < 1:
                retries += 1
                step.continue_steps = True
                await action(timeout=30000)
                async for page, context in self.next_step(page, step, remaining_steps, new_context):
                    yield page, context
            else:
                raise err

    async def handle_select(
        self,
        page: Page,
        step: PlaybookStep,
        remaining_steps: list[PlaybookStep],
        context: PlaybookContext,
    ) -> AsyncGenerator[tuple[Page, PlaybookContext], None]:
        for cstep in context:
            print("context", cstep)
        print("attempt", step)
        if step.choice == "SH_ALL":
            option_selector = f"{step.target} option"
            for option_label in await page.locator(option_selector).all_text_contents():
                if option_label.startswith("--"):
                    continue

                print("soption", option_label)
                await page.select_option(step.target, label=option_label)
                new_context = context + [
                    PlaybookStep(action=step.action, target=step.target, choice=option_label)
                ]
                async for page, context in self.next_step(page, step, remaining_steps, new_context):
                    yield page, context
        else:
            option_label = await page.locator(
                f"{step.target} option[value='{step.choice}']"
            ).text_content()
            if not option_label:
                raise Exception("Couldn't find option {step.choice} in select {step.target}")
            await page.select_option(step.target, value=step.choice)
            new_context = context + [
                PlaybookStep(action=step.action, target=step.target, choice=option_label)
            ]
            async for page, context in self.next_step(page, step, remaining_steps, new_context):
                yield page, context

    async def handle_click(
        self,
        page: Page,
        step: PlaybookStep,
        remaining_steps: list[PlaybookStep],
        context: PlaybookContext,
    ) -> AsyncGenerator[tuple[Page, PlaybookContext], None]:
        async def action(timeout):
            await page.wait_for_selector(step.target, timeout=timeout)
            await page.click(step.target)

        new_context = context + [step]
        async for page, context in self.execute_step(
            page, step, remaining_steps, new_context, action
        ):
            yield page, context

    async def handle_wait_for_nav(
        self,
        page: Page,
        step: PlaybookStep,
        remaining_steps: list[PlaybookStep],
        context: PlaybookContext,
    ) -> AsyncGenerator[tuple[Page, PlaybookContext], None]:
        new_context = context + [step]
        async for page, context in self.execute_step(
            page, step, remaining_steps, new_context, page.wait_for_load_state
        ):
            yield page, context
        await page.go_back()

    async def playbook_step(
        self, page: Page, steps: list[PlaybookStep], context: PlaybookContext
    ) -> AsyncGenerator[tuple[Page, PlaybookContext], None]:
        if not steps:
            return

        step, remaining_steps = steps[0], steps[1:]
        next_steps: AsyncGenerator[tuple[Page, PlaybookContext], None] | None = None
        if step.action == PlaybookAction.WAIT_FOR_NAV:
            next_steps = self.handle_wait_for_nav(page, step, remaining_steps, context)
        elif step.action == PlaybookAction.SELECT:
            next_steps = self.handle_select(page, step, remaining_steps, context)
        elif step.action == PlaybookAction.CLICK:
            next_steps = self.handle_click(page, step, remaining_steps, context)

        if not next_steps:
            raise Exception(f"could not handle step {step}")

        async for next_page, context in next_steps:
            yield next_page, context

    async def run_playbook(self, page: Page, skip_playbook: bool = False):
        if not self.playbook or skip_playbook:
            yield page, []
            return

        async for page, context in self.playbook_step(page, self.playbook, []):
            yield page, context
