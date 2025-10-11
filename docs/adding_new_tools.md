Adding new tools is an extremely easy process:

1. Go to `oatlas/tools`
2. Create a new directory, say `new_tool_x/`
3. Make files or directories as you need.

```py
class ClassName:
	@staticmethod
	def some_important_function_1(arguments):
		# Do something
		return

	@staticmethod
	def some_important_function_2(arguments):
		# Do something
		return
```

4. Now head over to `oatlas/core/lib/functions.py`. Add an entry for the class there and the functions defined inside the class. Make sure to add the class correctly inside `class_function_dict`. This is for bookkeeping.
5. Edit the `oatlas/tools/__init__.py` file and import the engine name there.
6. Update the `oatlas/methods/methods.yaml` file as well with whatever you have added.
7. Create description for your functions over at `oatlas/utils/tool_descriptions`