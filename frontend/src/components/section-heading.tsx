import type { ReactNode } from 'react';

export function SectionHeading({
	title,
	description,
	action,
}: {
	title: string;
	description: string;
	action?: ReactNode;
}) {
	return (
		<div className="mb-5 flex flex-wrap items-start justify-between gap-4">
			<div>
				<h1 className="text-foreground text-[1.65rem] leading-tight font-semibold tracking-tight sm:text-[2.1rem]">
					{title}
				</h1>
				<p className="text-muted-foreground mt-1.5 max-w-prose text-sm">{description}</p>
			</div>
			{action}
		</div>
	);
}
