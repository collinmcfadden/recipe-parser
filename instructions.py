from abc import ABC, abstractmethod

class InstructionsBase(ABC):
	
	@abstractmethod
	def add_instruction(self, details):
		pass

	@abstractmethod
	def get_json(self):
		pass

	
class Steps(InstructionsBase):

	def __init__(self):
		self.type = "steps"
		self.steps = []

	def add_instruction(self, details):
		self.steps.append({"details": {"S": details}})

	def get_json(self):
		return {
			"type": {"S": self.type},
			"steps": self.steps
		}

	
class SplitSteps(InstructionsBase):

	def __init__(self):
		self.type = "split_steps"
		self.split_steps = []
		self.current_section = None

	def set_section_title(self, title):
		if self.current_section is not None:
			self.split_steps.append(self.current_section)

		self.current_section = {
			"title": {"S": title},
			"steps": []
		}

	def add_instruction(self, details):
		self.current_section["steps"].append({"details": {"S": details}})

	def get_json(self):
		if self.current_section is not None:
			self.split_steps.append(self.current_section)
			self.current_section = None

		return {
			"type": {"S": self.type},
			"split_steps": self.split_steps
		}
