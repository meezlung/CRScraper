<script>
	import { onMount } from 'svelte';
    import { get } from 'svelte/store';
	// --------------- For login ---------------
	let crs_username = '';
	let crs_password = '';
	let isAuthenticated = false;
	let errorMessage = '';

	async function handleLogin() {
		try {
			const res = await fetch('http://localhost:8080/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username: crs_username, password: crs_password })  // Corrected keys here
			});
			const result = await res.json();

			if (result.status === "success") {
				isAuthenticated = true;
				// await getSchedules(); // Fetch schedules upon successful login
			} else {
				errorMessage = 'Login failed. Please check your credentials.';
			}
		} catch (error) {
			errorMessage = 'Error logging in. Please try again.';
			console.error(error);
		}
	}
	// -----------------------------------------


	// ----------- For setting URLS ------------
	let courseURLs = '';
	let urlMessage = '';
	let urlsSet = false;

	async function setURLs() {
		// Check if the input is empty
		if (!courseURLs.trim()) {
			urlMessage = "Please enter at least one URL before setting.";
			return; // Exit the function early if the input is empty
		}

		try {
			const res = await fetch('http://localhost:8080/set-urls', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ links: courseURLs })
			});
			const result = await res.json();

			if (result.status === "success") {
				urlMessage = "URLs successfully set!";
				urlsSet = true; // Mark URLs as set
			} else {
				urlMessage = "Failed to set URLs. Please check your input.";
			}
		} catch (error) {
			urlMessage = "Error setting URLs. Please try again.";
			console.error(error);
		}
	}
	// -----------------------------------------


	// --------- For getting schedules ----------
	let schedules = [];
	let scheduleGroups = [];
	let visibleCount = 3;

	async function getSchedules() {
		if (!urlsSet) {
			urlMessage = "Please set course URLs first before fetching schedules.";
			return; // Exit the function early if URLs are not set
		}

		try {
			const scrapeResponse = await fetch('http://localhost:8080/scrape', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});
			const scrapeResult = await scrapeResponse.json();

			if (scrapeResult.status === "success") {
				const scheduleResponse = await fetch('http://localhost:8080/get-schedule');
				schedules = await scheduleResponse.json();
				groupSchedules();
			} else {
				urlMessage = "Failed to generate schedule data.";
			}
		} catch (error) {
			urlMessage = "Failed to generate schedule data.";
			console.error('Error during scraping or fetching schedules:', error);
		}
	}

	function groupSchedules() {
		let currentGroup = [];

		Array.isArray(schedules) && schedules.forEach(schedule => { // Make sure schedules is an array
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

	// getSchedules(); // Fetch schedules upon component mount

	function showMore() {
		visibleCount += 5;
	}
	// -----------------------------------------
</script>

<main>
	{#if isAuthenticated}
		<div class="container">
			<div class="box" id="course-urls-box">
				<!-- Input page for Course URLs -->
				<h1>Enter Course URLs</h1>
				<input type="text" id="course-urls" placeholder="Enter URLs, separated by commas" bind:value={courseURLs} />
				<button on:click={setURLs}>Set URLs</button>

				{#if urlMessage == "URLs successfully set!"}
					<p style="color: green;">{urlMessage}</p>
				{:else}
					<p style="color: red;">{urlMessage}</p>
				{/if}
			</div>

			<div class="box" id="schedule-list-box">
				<!-- Schedule List -->
				<h1>Schedule List</h1>
				<button on:click={getSchedules}>Fetch Schedules</button>

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
										{#if group.averageProbability == "N/A"}
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
					{#if visibleCount < scheduleGroups.length}
						<button on:click={showMore}>Show More</button>
					{/if}
				</div>
			</div>	
		</div>

	{:else}
		<!-- Login page -->
		<h1>Login</h1>
		<h2>These login credentials will be used for logging in your CRS and extract enlistment courses.</h2>
		<form on:submit|preventDefault={handleLogin}>
			<div>
				<label for="username">Username:</label>
				<input type="text" id="username" bind:value={crs_username} required />
			</div>
			<div>
				<label for="password">Password:</label>
				<input type="password" id="password" bind:value={crs_password} required />
			</div>
			<button type="submit">Login</button>
			{#if errorMessage}
				<p style="color: red;">{errorMessage}</p>
			{/if}
		</form>
	{/if}
</main>

<style>
	/* --------------- For login --------------- */
	form {
		display: flex;
		flex-direction: column;
		align-items: center;
		background-color: #f9f9f9;
		border: 1px solid #ddd;
		padding: 2em;
		border-radius: 10px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
		max-width: 400px;
		margin: 0 auto;
	}

	label {
		margin-bottom: 0.5em;
		font-weight: bold;
		color: #333;
		font-size: 1em;
	}

	input[type="text"],
	input[type="password"] {
		width: 100%;
		padding: 0.75em;
		margin-bottom: 1em;
		border: 1px solid #ccc;
		border-radius: 5px;
		font-size: 1em;
		box-sizing: border-box;
		transition: border-color 0.3s;
	}


	input[type="text"]:focus,
	input[type="password"]:focus {
		border-color: #ff3e00;
		outline: none;
		box-shadow: 0 0 5px rgba(255, 62, 0, 0.2);
	}
	
	button[type="submit"] {
		width: 100%;
		padding: 0.75em;
		border: none;
		background-color: #ff3e00;
		color: white;
		font-size: 1em;
		font-weight: bold;
		border-radius: 5px;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	button[type="submit"]:hover {
		background-color: #e53600;
	}

	/* Error message styling */
	p[style="color: red;"] {
		color: #ff4d4d;
		margin-top: 1em;
		font-size: 0.9em;
		font-weight: bold;
		text-align: center;
	}

	/* Responsive styling */
	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
	/* ----------------------------------------- */


	.container {
		display: flex;
		justify-content: space-between;
		padding: 20px;
		margin-top: 20px;
	}

	.box {
		width: 45%;
		padding: 20px;
		border: 2px solid #ddd;
		border-radius: 10px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
		background-color: #f9f9f9;
	}

	/* --------------- For course URLs --------------- */
	/* #course-urls-box {
		background-color: #e7f7ff;
		height: 600px;
	} */

	#course-urls {
		width: 100%;
		padding: 10px;
		margin-top: 10px;
		font-size: 16px;
		border-radius: 5px;
		border: 1px solid #ddd;
	}
	/* ----------------------------------------------- */
	

	/* -------------- Schedule List ------------ */
	/* #schedule-list-box {
		background-color: #eaf9e7;
		height: 600px;
	} */

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
	/* ----------------------------------------- */
</style>
