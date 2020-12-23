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
		self.steps.append({"M": {"details": {"S": details}}})

	def get_json(self):
		return {"M": {
			"type": {"S": self.type},
			"steps": {"L": self.steps}
			}
		}

	
class SplitSteps(InstructionsBase):

	def __init__(self):
		self.type = "split_steps"
		self.split_steps = []
		self.current_section = None

	def set_section_title(self, title):
		if self.current_section is not None:
			self.split_steps.append({"M": self.current_section})

		self.current_section = {
			"title": {"S": title},
			"steps": {"L": []}
		}

	def add_instruction(self, details):
		self.current_section["steps"]["L"].append({"M": {"details": {"S": details}}})

	def get_json(self):
		if self.current_section is not None:
			self.split_steps.append({"M": self.current_section})
			self.current_section = None

		return {"M": {
			"type": {"S": self.type},
			"split_steps": {"L": self.split_steps}
			}
		}
