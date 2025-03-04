from typing import Tuple, Iterator, Optional, List

from edi_835_parser.segments.service import Service as ServiceSegment
from edi_835_parser.segments.claim import Claim as ClaimSegment
from edi_835_parser.segments.date import Date as DateSegment
from edi_835_parser.segments.reference import Reference as ReferenceSegment
from edi_835_parser.segments.amount import Amount as AmountSegment
from edi_835_parser.segments.adjustment import Adjustment as ServiceAdjustmentSegment
from edi_835_parser.segments.remark import Remark as RemarkSegment
from edi_835_parser.segments.utilities import find_identifier
from edi_835_parser.segments.provider_adjustment import ProviderAdjustment as ProviderAdjustmentSegment

from log_conf import Logger


class Service:
	initiating_identifier = ServiceSegment.identification
	terminating_identifiers = [
		ServiceSegment.identification,
		ClaimSegment.identification, ProviderAdjustmentSegment.identification,
		'SE'
	]

	def __init__(
			self,
			service: ServiceSegment = None,
			dates: List[DateSegment] = None,
			references: List[ReferenceSegment] = None,
			remarks: List[RemarkSegment] = None,
			amount: AmountSegment = None,
			adjustments: List[ServiceAdjustmentSegment] = None
	):
		self.service = service
		self.dates = dates if dates else []
		self.references = references if references else []
		self.remarks = remarks if remarks else []
		self.amount = amount
		self.adjustments = adjustments if adjustments else []

	def __repr__(self):
		return '\n'.join(str(item) for item in self.__dict__.items())

	@property
	def allowed_amount(self):
		if self.amount:
			if self.amount.qualifier == 'allowed - actual':
				return self.amount.amount

	@property
	def service_date(self) -> Optional[DateSegment]:
		service_date = [d for d in self.dates if d.qualifier == 'service']
		assert len(service_date) <= 1, f'{self.dates}'

		if len(service_date) == 1:
			return service_date[0]

	@property
	def service_period_start(self) -> Optional[DateSegment]:
		service_period_start = [d for d in self.dates if d.qualifier == 'service period start']
		assert len(service_period_start) <= 1, f'{self.dates}'

		if len(service_period_start) == 1:
			return service_period_start[0]
		else:
			return self.service_date

	@property
	def service_period_end(self) -> Optional[DateSegment]:
		service_period_end = [d for d in self.dates if d.qualifier == 'service period end']
		assert len(service_period_end) <= 1

		if len(service_period_end) == 1:
			return service_period_end[0]
		else:
			return self.service_date

	@property
	def service_identification(self) -> Optional[ReferenceSegment]:
		service_id = [r for r in self.references if r.qualifier == 'provider control number']
		assert len(service_id) <= 1

		if len(service_id) == 1:
			return service_id[0]

	@property
	def rendering_provider(self) -> Optional[ReferenceSegment]:
		rendering_provider_qualifier_code = ['OB', '1A', '1B', '1C', '1D', '1G', '1H', '1J', 'D3', 'G2', 'HPI', 'SY']
		rendering_provider = [r for r in self.references if r.qualifier_code in rendering_provider_qualifier_code]
		assert len(rendering_provider) <= 1

		if len(rendering_provider) == 1:
			return rendering_provider[0]



	@classmethod
	def build(cls, segment: str, segments: Iterator[str]) -> Tuple['Service', Optional[str], Optional[Iterator[str]]]:
		service = Service()
		service.service = ServiceSegment(segment)

		while True:
			try:
				segment = segments.__next__()
				identifier = find_identifier(segment)

				if identifier == DateSegment.identification:
					date = DateSegment(segment)
					service.dates.append(date)

				elif identifier == AmountSegment.identification:
					service.amount = AmountSegment(segment)

				elif identifier == RemarkSegment.identification:
					remark = RemarkSegment(segment)
					service.remarks.append(remark)

				elif identifier == ReferenceSegment.identification:
					reference = ReferenceSegment(segment)
					service.references.append(reference)

				elif identifier == ServiceAdjustmentSegment.identification:
					service.adjustments.append(ServiceAdjustmentSegment(segment))

				elif identifier in cls.terminating_identifiers:
					return service, segment, segments

				else:
					message = f'Identifier: {identifier} not handled in service loop.'
					Logger.logr.warning(message)

			except StopIteration:
				return service, None, None


if __name__ == '__main__':
	pass
