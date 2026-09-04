---
name: qrafig-desktop-wpf
description: Work on QRAFIG Desktop's WPF and XAML safely — the defect classes that compile cleanly and only fail at run time (a StaticResource that does not exist, a DataContext override that shadows a sibling binding, a property Trigger on the object-typed Tag, a control with no style, a command that never re-asks whether it may execute, an Auto column that starves its neighbour), the design-system resource conventions, dispatcher and collection threading, layout and virtualization, and a repeatable static audit that finds several of them before the live run. Use for any XAML, view, resource dictionary, converter, style, template or rendering change.
when_to_use: Editing a .xaml file, a view, a converter, a style or the theme; a control that does not appear, does not highlight, is clipped, is the wrong colour, or a button that is permanently disabled; "fix this WPF page"; binding errors.
---

# WPF and XAML in QRAFIG Desktop

> **What compiles is not what renders** (ADR-0191). One Linux build compiled the markup and reasonably
> concluded it "binds to names that exist". The next Windows run found **eleven** defects in the same
> markup, **nine** of which no test in this repository could have caught.

WPF on `net10.0-windows`, one `QRAFIG.exe`, a hand-written thirty-line MVVM base class and **no MVVM
toolkit** — deliberately, because the view models live in a project with no UI-framework reference so
they can be tested with no dispatcher (ADR-0109). **Generic WPF advice that begins "install
CommunityToolkit.Mvvm" does not apply here.** Neither does WinUI 3 or WPF→WinUI migration guidance:
WinUI was evaluated and rejected for this product.

## The three defect classes the live run exists to find

### 1. Resolution — the name exists in BAML and not at run time

- **A `StaticResource` key that is defined nowhere.** BAML compiles without resolving it. At run time
  the first one throws inside `InitializeComponent()`, so `new SomeView(...)` never returns — and
  because navigation runs through a `TwoWay` binding's source setter, the WPF binding engine
  **swallows the exception**. The sidebar highlights the workspace, the breadcrumb says the workspace,
  and the previous one stays on screen. No log line, no dialog, no crash.
- **A `DataContext` override on the same element as another binding**, which silently shadows it.
  Five Finance sections were permanently visible and stacked for exactly this reason.
- **A style applied to a control its `TargetType` does not name** — `Placeholder.Panel` on a `Border`
  when it targets `StackPanel` throws at XAML load, and the shell keeps showing the previous
  workspace while the sidebar says otherwise.
- **A `TwoWay` binding onto a get-only property.**

The **fixed** shape for a section that re-points its `DataContext` is to root the sibling binding
explicitly through the `UserControl`:

```xml
<Grid Visibility="{Binding DataContext.IsRegister,
                   RelativeSource={RelativeSource AncestorType={x:Type UserControl}},
                   Converter={StaticResource Visible}}"
      DataContext="{Binding Register}">
```

A section that asked its **own** `DataContext` whether it should be visible is asking the register
whether the workspace is showing the register — which it cannot answer, so every section renders at
once.

### 2. Theming — the control has no style

`ListView` and `ListBox` once had none, so six Customers lists and the till's customer results rendered
in WPF's white default inside a dark window. Implicit styles live in
`desktop/src/Qrafig.Desktop/Theme/Controls.xaml` and apply application-wide; a new control type needs
one there.

**No hard-coded colour, size or radius in any view.** Every reference is a `DynamicResource`, which is
what lets the theme swap repaint live controls (`Theme/Tokens.Light.xaml`, `Theme/Tokens.Dark.xaml`,
`ThemeManager`). Both palettes carry **identical key sets**; adding a token to one and not the other
is a defect in the other theme only, which is exactly the kind that ships.

Resource keys are dotted and namespaced by role — `Text.Numeric`, `Button.Subtle`, `Surface.Raised`,
`Border.Subtle`, `State.Selected`, `Accent.Default`, `Card`, `Card.Kpi`. Follow the convention; a
plausible-sounding neighbour of a real key is precisely the failure mode.

### 3. Liveness — it renders, and it does nothing

- **A command that never re-asks whether it may execute.** `RelayCommand` and `AsyncCommand` raise
  `CanExecuteChanged` only when something calls `RaiseCanExecuteChanged()`, deliberately —
  `CommandManager.RequerySuggested` is a `PresentationCore` type that would drag a dispatcher into the
  UI-framework-free layer. Four Customers view models never called it, across forty commands: Edit,
  Reload, Save, Record payment and Write off were **disabled permanently** and the register was in
  practice read-only. Nothing caught it, because no test asks a WPF button whether it is enabled.

  **The rule (ADR-0190): if a command's `CanExecute` reads anything, something must tell it when that
  thing changed.** The safe pattern is the Customers one — each view model subscribes to **its own**
  `PropertyChanged` and re-raises **every** command from there: one call site, and it cannot miss a
  dependency. A command whose `CanExecute` reads *another* view model's state subscribes to that one.
- **A control bound to nothing at all**, or to a `Tag` the theme never draws.
- **A property `Trigger` on `Tag`.** `Tag` is typed `object`, so `<Trigger Property="Tag" Value="True">`
  compares a boxed `bool` against the **string** `"True"` and never matches — the tab strip renders
  with nothing selected, in every theme, silently. Use a `DataTrigger`:

  ```xml
  <DataTrigger Binding="{Binding RelativeSource={RelativeSource Self}, Path=Tag}" Value="True">
  ```

  (A `Tag` that genuinely holds a string, as `WindowChrome` does for native hover states, is fine.)
- **An `Auto` column that starves its neighbour**, or columns whose widths sum to exactly the
  container's, so the last one is clipped. A currency code cut in half — `14 650,00 AZ` — is precisely
  the ambiguity the per-currency rule exists to prevent.
- **A danger notice bound to "is composing"**, so opening any form renders an empty red alarm box
  before the operator has typed a character. An editor says nothing is wrong until something is.
- **A column bound to "is a card open" that also hides the create form**, so a business with nothing
  selected cannot add its first record.
- **A host that only one code path ever fills.** The shell's workspace hosts swap on `HasLock`, but
  only navigation filled the lock host — so a workspace that became unreachable *where it stood* went
  completely blank. Not zeros: nothing. Check every path that can enter a state, not just the usual one.

## Threading

**WPF marshals `PropertyChanged` for a binding by itself. It does *not* marshal `CollectionChanged`**
(ADR-0132). Any background work that updates a bound list must go through **`IUiThread`** — a port in
the UI-framework-free application layer, satisfied by the WPF dispatcher in the shell and claimed once
at startup. `ObservableList<T>.Replace` and `AddRange` run through it, and the **whole operation** is
marshalled, not just the notification: sending the event across while rebuilding the list on a
background thread would leave the UI thread free to enumerate a collection halfway through being
replaced — rarer than the exception and worse.

It is **ambient** rather than injected. Unset, it runs inline, which is exactly right for a test.

## The static audit

```bash
python .claude/skills/qrafig-desktop-wpf/scripts/xaml_audit.py .
```

It checks: undefined `StaticResource` keys; a style applied to the wrong `TargetType`;
`<Trigger Property="Tag" Value="True|False">`; a `DataContext` override beside an **un-rooted**
sibling binding; a list control with neither a `Style` nor an implicit style; and a `TwoWay` binding
with no path.

It is a **pre-filter, not a gate**. Every finding is a question — confirm it against the file, then
confirm the behaviour in the live run. It cannot see layout, focus, clipping, virtualization or a
command that never re-asks.

## Layout, lists and input

- **Grid sizing**: give the growing column `*` and the fixed one `Auto` or an explicit width, and
  check the total against the narrowest supported layout. QRAFIG's evidence bar is 100% and 150%
  scaling and a **1280×720 DIP laptop layout**.
- **Virtualization** is why WPF was chosen — `DataGrid` is well understood at twenty thousand rows.
  Do not put a virtualizing list inside a `StackPanel` or an unbounded `ScrollViewer`; that measures
  every item and destroys it.
- **Keyboard**: the till must be workable without a mouse. Check tab order, focus after a dialog
  closes, `Ctrl+K`, and that a command reachable by keyboard is also enabled.
- **Standard window chrome is deliberate** — snap layouts, the system menu and high-contrast themes
  are kept. Do not replace it with a custom title bar.
- Accessibility: full `UIAutomation` is one of the reasons for WPF. Do not remove automation names or
  replace a real control with a hand-drawn one.

## Read first

- `desktop/src/Qrafig.Desktop/Theme/` — `Tokens.Light.xaml`, `Tokens.Dark.xaml`, `Primitives.xaml`,
  `Controls.xaml`, `States.xaml`, `Navigation.xaml`, `WindowChrome.xaml`, `ThemeManager.cs`.
- `desktop/src/Qrafig.Desktop/Views/EmployeesView.xaml` — the **corrected** idioms, with comments
  explaining why each is what it is. Copy from here, not from the older views.
- `desktop/src/Qrafig.Desktop/Converters/`.
- `docs/implementation-status.md` → the handoff row, which lists the live-run defects found so far and
  any **defect carried forward**.
- ADR-0109, ADR-0132, ADR-0190, ADR-0191.

## Verification

Build (0 warnings); the static audit; `desktop/tests/Qrafig.Desktop.Tests`; and — **mandatory for any
XAML, view, resource, converter, command or shell change** — a live `QRAFIG.exe` smoke on Windows. See
`qrafig-desktop-live-smoke`. Headless tests cannot close this gap; do not try to substitute more of them.

## Do not

- Do not introduce an MVVM toolkit or any dependency that drags `PresentationCore` into
  `Qrafig.Desktop.Application`.
- Do not hard-code a colour, size or radius in a view.
- Do not add a token to one theme dictionary only.
- Do not set `DataContext` and another un-rooted binding on one element.
- Do not use a property `Trigger` on `Tag` for a boolean.
- Do not update a bound collection off the UI thread without `IUiThread`.
- Do not use `Dispatcher` directly from the application layer.
- Do not claim a Desktop change complete because it compiled.
- Do not import WinUI or WPF→WinUI migration guidance.

## Related skills

`qrafig-desktop-workspace` (navigation, access states, contracts) · `qrafig-desktop-live-smoke`
(the gate) · `qrafig-testing` · `qrafig-performance` · `qrafig-diagnostics`.
