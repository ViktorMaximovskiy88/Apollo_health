# ReactDataGrid local docs

## Why does this document exist?

ReactDataGrid is not easy to use. The docs are not easy to read, and the source code is atrocious. This document exists to make it easier for our team's developers to quickly deal with situations our coworkers have already dealt with.

---

## If it's so hard to use, why do we use it at all?

Matt (the architect) has a good response to this question:

> Things we need from our data table:
>
> - Row Virtualization
> - Column Level Filtering for Text, Numerics, Levels (checkboxes) and Dates
> - Row selection (a.k.a find an row and hit enter to go to that site's page)
> - Server Side Pagination (ideally 'infinite scroll' pagination)
> - Export to CSV/Excel
> - Multi Column Sort
>
> All of this is possible with react-table of course, but I reviewed using react-table (and react-data-grid and ag-grid and many others) and determined the time to get all of that working well was not worth the investment.

---

## What do I need to know that the docs won't easily tell me?

Think of this datatable as a form. It has uncontrolled elements and controlled elements. Virtually anything in it can be either controlled or uncontrolled, and, for our purposes, most things you work with are going to either be controlled, or you will switch it from controlled to uncontrolled.

And remember that whenever you make something controlled like filtering or sorting, you will likely have to manually change the data fed into `dataSource`. This is usually easier than you think to do. The hard thing is to remember that you need to do it.

---

## Why do we use the redux `store` so much for controlling things like filtering and sorting in the datatable?

Matt (the architect) has a good response:

> You want to keep your current filters when you click around, and if it's in local state you lose it when the component unmounts.
>
> For example if you filter to `taskStatus='FAILED'`, you want to click into each one and see what's wrong with it, if it resets every time you go back to `/sites` you'd go crazy.
