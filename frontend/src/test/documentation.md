# Testing Documentation

---

#### Purpose

This documentation exists to explain idiosyncracies of testing our application that cannot be spelled out in the test code, itself.

---

#### ReactDataGrid

Testing can be difficult with `ReactDataGrid`. A few things to remember:

- Anytime you `render()` a component with a `ReactDataGrid` in it, make sure to wrap that `render()` in a promise and an `act()`. (For more on why, check [this article](https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning#an-alternative-waiting-for-the-mocked-promise)). Here is an example from `src/features/collections/CollectionsPage.test.tsx`:

```ts
const dataGridDoneRendering = Promise.resolve();
render(<CollectionsPage isVirtualized={false} />);
await act(async () => {
  await dataGridDoneRendering;
});
```

- Test only the top element in the table because, by default, `ReactDataGrid` will only render that first row. This is because `ReactDataGrid` [is virtualized by default](https://reactdatagrid.io/docs/api-reference#props-virtualized). We have tried manually increasing the viewport, but the only way to render more rows is to pass a prop: `virtualized={false}` into the `ReactDataGrid` component. However, if you can get away with only testing the top-most rendered row, please do so to prevent polluting the non-test code with test code.

---

### Noteable articles

Noteable articles for testing with `jest`, `@testing-library`, and `msw`:

- [Fix the "not wrapped in act(...)" warning.](https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning) This warning is ubiquitous when doing tests with `@testing-library`. This article is your friend.
- [Common mistakes with React Testing Library.](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library) These are _extremely_ common mistakes when writing tests with `@testing-library`. I know a developer who has been using this library since it came out, and he's still been making at least one of these mistakes. It's all very good advice.
- [The testing trophy and testing classification](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications) is a more high-level, philosophical overview of a good way to think about testing. Frontend testing that we do generally refers to Dodds' "integration" and "unit" testing, but he also makes reference to end-to-end testing with `cypress` or `playwright` and what he calls "static testing" with typescript and/or eslint.

---

### Noteable Github Repos

- [This github repo](https://github.com/kentcdodds/testing-react-apps) has several really good exercises for learning how to write frontend tests with `jest`, `@testing-library`, and `msw`. It's also an extremely good reference. Do be weary, however, of copying code from this repo because of the license it's under.
  - There are also videos that go along with this repo, but they are part of a paid resource known as [Epic React](https://epicreact.dev/). If you are reading this and Paul Getsy is your manager, it's extremely likely he can purchase the entire course for you if you think you'll go through it. It's an extremely good course.
- [This github repo](https://github.com/kentcdodds/jest-cypress-react-babel-webpack/tree/tjs/jest-23) is another good resource to reference. It is best for understanding both how to scale testing to larger projects and also how to write effective configuration for testing. Also be weary of copying code because of the license this code is under.
  - There are videos associated with this repo, but they are part of a paid resource known as [Testing Javascript](https://testingjavascript.com/). It's not as good as Epic React, however.
