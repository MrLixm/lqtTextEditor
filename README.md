# lqtTextEditor

More complexes text editor in PyQt.

# LinePlainTextEdit

Works well for code editing. Add suport for :
- line numbering in sidebar
  - range selection of lines from the sidebar 
- indentation and unindentation with custom characters
- line hiding/showing/isolating

![demo gif of using the LinenumberedTextEditor](.\doc\img\LinenumberedTextEditor.demo.gif)

See [test_numbered.py](tests/test_numbered.py) for an example.

## Styling 

With stylesheet :

```css
/*dark theme*/
QWidget.LineSideBarWidget{
  font-family: monospace;
  color: rgb(150,150,150);
  background-color: rgb(55,55,58);
  border-right: 1px solid rgb(60,60,60);
}
QWidget.LinePlainTextEdit{
  font-family: monospace;
  color: rgb(200,200,200);
  background-color: rgb(50,50,55);
}
```