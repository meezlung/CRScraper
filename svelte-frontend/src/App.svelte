<script>
	let schedules = [];
	let scheduleGroups = [];
	let visibleCount = 3;

	async function getSchedules() {
		const res = await fetch('http://localhost:8080/get-schedule');
		schedules = await res.json();
		groupSchedules();
	}

	function groupSchedules() {
		let currentGroup = [];

		schedules.forEach(schedule => {
			if (!schedule.Course) {
				if (currentGroup.length > 0) {
					// Calculate average probability for the group
					const averageProbability = calculateAverageProbability(currentGroup);
					scheduleGroups = [...scheduleGroups, { schedules: currentGroup, averageProbability }];
					currentGroup = [];
				}
			} else {
				currentGroup.push(schedule);
			}
		});

		if (currentGroup.length > 0) {
			const averageProbability = calculateAverageProbability(currentGroup);
			scheduleGroups = [...scheduleGroups, { schedules: currentGroup, averageProbability }];
		}
	}

	function calculateAverageProbability(group) {
		// Check if any schedule in the group has a probability of -1.0
		if (group.some(schedule => parseFloat(schedule.Probability) === -100.0)) {
			return 'N/A';
		}

		// Filter out schedules with empty probability values
		const validSchedules = group.filter(schedule => schedule.Probability !== "");

		// Calculate the sum of valid probabilities
		const total = validSchedules.reduce((sum, schedule) => {
			const probability = parseFloat(schedule.Probability) || 0;
			return sum + probability;
		}, 0);

		// Calculate and return the average, rounded to 3 decimal places
		return validSchedules.length > 0 ? (total / validSchedules.length).toFixed(4) : 'N/A';
	}

	getSchedules();

	function showMore() {
		visibleCount += 5;
	}
</script>

<main>
	<h1>Schedule List</h1>
	<div class="schedule-box-big">
		{#each scheduleGroups.slice(0, visibleCount) as group}
			<div class="schedule-box-small">
				<table class="schedule-table">
					<thead>
						<tr>
							<th>Course</th>
							<th>Section</th>
							<th>Day</th>
							<th>Time</th>
							<th>Probability</th>
						</tr>
					</thead>
					<tbody>
						{#each group.schedules as schedule}
							{#if schedule.Probability}
								<tr>
									<td>{schedule.Course}</td>
									<td>{schedule.Section}</td>
									<td>{schedule.Day}</td>
									<td>{schedule.Time}</td>
									<td>{schedule.Probability}%</td>
								</tr>
							{:else}
								<tr>
									<td>{schedule.Course}</td>
									<td>{schedule.Section}</td>
									<td>{schedule.Day}</td>
									<td>{schedule.Time}</td>
									<td>{schedule.Probability}</td>
								</tr>
							{/if}
						{/each}
						<tr class="average-row">
							{#if group.averageProbability === 'N/A'}
								<td colspan="4"><strong>Average Probability</strong></td>
								<td><strong>{group.averageProbability}</strong></td>
							{:else}
								<td colspan="4"><strong>Average Probability</strong></td>
								<td><strong>{group.averageProbability}%</strong></td>
							{/if}
						</tr>
					</tbody>
				</table>
				<br />
			</div>
		{/each}
	</div>

	{#if visibleCount < scheduleGroups.length}
		<button on:click={showMore}>Show More</button>
	{/if}
</main>

<style>
	.schedule-table {
		width: 100%;
		max-width: 600px;
		margin: 1em auto;
		border-collapse: collapse;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}
	
	.schedule-table:hover {
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}
	
	.schedule-table th,
	.schedule-table td {
		border: 1px solid #ddd;
		padding: 0.5em;
		text-align: center;
	}
	
	.schedule-table th {
		background-color: #f4f4f4;
		font-weight: bold;
	}
	
	.schedule-table tr:nth-child(even) {
		background-color: #f9f9f9;
	}

	.average-row {
		background-color: #ffecec;
		font-weight: bold;
	}

	.schedule-box-big {
		border: 1px solid #ddd;
		padding: 1em;
		margin: 0.5em auto; /* Center the box */ 
		max-width: 700px;	
		max-height: 500px; /* Set a maximum height */
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		overflow-y: auto; /* Add vertical scroll bar */
		scroll-behavior: smooth; /* Smooth scrolling */
	}

	button {
		margin: 1em 0;
		padding: 0.5em 1em;
		border: none;
		background-color: #ff3e00;
		color: white;
		border-radius: 4px;
		cursor: pointer;
	}
	button:hover {
		background-color: #e53600;
	}
	
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 2em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
