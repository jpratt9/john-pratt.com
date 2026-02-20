---
title: "Cloud-Based Application Development Made Simple"
date: '2025-09-14'
description: "A practical guide to cloud-based application development. Learn to build modern, scalable, and cost-effective solutions with expert insights and clear examples."
draft: false
slug: '/cloud-based-application-development'
tags:

  - cloud-based-application-development
  - cloud-native-architecture
  - cloud-services
  - SaaS-development
  - microservices
---

![Article Header Image](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/cloud-based-application-development/featured-image-4dfd5043-b36b-48ba-875c-f23f61aeb39a.jpg)

Think about setting up a new business. You could go the old-school route: buy land, pour a foundation, build an office from the ground up, and manage your own power and water. Or, you could lease a space in a high-tech office building where all of that is handled for you.

That's the fundamental shift behind **cloud-based application development**. It's the decision to build and run your software on a global network of powerful servers instead of buying and managing your own physical hardware.

## Why This Approach Changes Everything

Moving to the cloud is much more than a simple tech upgrade. It's a strategic move that introduces a whole new level of speed, efficiency, and scale to your business. Instead of tying up huge amounts of cash in physical servers that are outdated almost as soon as you buy them, you can tap into world-class infrastructure on a simple pay-as-you-go model.

This flips the script from heavy capital expenditure (CapEx) to a more flexible operational expenditure (OpEx). It frees up cash, slashes financial risk, and lets even a small startup go toe-to-toe with industry giants.

![Image](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/cloud-based-application-development/dad51d47-c27c-4343-8ba7-affe84175d06.jpg)

Ultimately, this model lets your team focus on what actually matters: building great products for your customers. When you hand off the headache of infrastructure management to cloud providers like [Amazon Web Services (AWS)](https://aws.amazon.com/), [Microsoft Azure](https://azure.microsoft.com/en-us/), or [Google Cloud](https://cloud.google.com/), your developers can pour their energy into creating new features, polishing the user experience, and just plain innovating faster.

### The Core Business Advantages

The benefits go way beyond just saving a few bucks on hardware. When you adopt a cloud-first approach, you fundamentally change how your business runs and grows.

* **Unmatched Scalability:** Cloud apps can automatically add or remove resources to perfectly match user demand. This means you're not paying for servers to sit idle during slow periods, but you can also handle a massive, unexpected surge in traffic without your service crashing.
* **Global Reach in Minutes:** Need to serve customers in Europe or Asia? It's no longer a months-long project. Cloud providers have data centers all over the world, letting you deliver a fast, responsive experience to users anywhere on the planet.
* **Accelerated Innovation:** Your team gets instant access to a massive toolbox of managed services - everything from powerful databases and AI tools to complex analytics engines. This lets you build incredibly sophisticated apps without needing an in-house expert for every single piece of the puzzle.
* **Enhanced Reliability and Security:** Cloud platforms invest billions in security and backup systems, providing a level of resilience that most individual companies could never dream of building on their own.

> By getting rid of the old friction points of traditional IT, cloud-based development gives businesses the freedom to test new ideas, change direction on a dime, and react to the market with incredible speed.

At its core, this transition is about building for what's next. It's about creating systems that are not only powerful today but are flexible enough to evolve with future demands. The cloud is the foundation for resilient, cost-effective, and globally available applications that can grow right alongside your ambition. It's the engine that powers nearly every modern digital experience you use.

## Understanding the Building Blocks of the Cloud

To really get the most out of building applications for the cloud, you first have to grasp the core concepts that make it all tick. These aren't just buzzwords; they represent a fundamental change in how we think about, design, and launch software. Moving to the cloud is less about *where* your code is running and more about *how* it's built to be resilient and ready for growth.

This strategic shift is what's behind the explosive growth we're seeing. The global cloud computing market is on a trajectory to more than triple, projected to climb from **USD 500 billion** in 2023 to an incredible **USD 1.6 trillion** by 2030. This isn't just hype; it's driven by real-world advantages like potential cost savings of up to **30%** over traditional IT. A quick look at cloud migration statistics shows just how widespread this move has become.

![Image](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/cloud-based-application-development/085e3c47-d06c-4132-b359-77501ddad474.jpg)

### Microservices: The LEGO Approach to Software

Think about building a complex model. You could try carving it from a single, massive block of wood - what we'd call a monolith. It might look solid, but what happens when you need to change one tiny detail? You risk cracking the entire thing. For a long time, this was how we built software.

Microservices offer a much smarter alternative. It's like building with individual LEGO bricks. Each piece of your application - user logins, payment processing, the search function - is its own small, independent "service," or brick.

This structure gives you incredible flexibility:

* **Independent Updates:** You can swap out or upgrade the payment brick without ever touching the login brick. This makes updates faster and far less risky.
* **Technology Freedom:** One team can build their service in Python while another uses Java. You can always use the best tool for that specific job.
* **Fault Isolation:** If one LEGO brick happens to fail, it doesn't cause the whole model to collapse. The rest of the app keeps running, which makes the entire system much more resilient.

This approach has become central to modern cloud development because it lets teams build huge, complex applications that are far easier to manage, scale, and improve over time.

### Containers: Standardized Shipping for Your Code

So you've got all your microservices built. Now, how do you make sure they run the same way everywhere, from your laptop to the live servers? That's where containers come in.

Think of a container as a standardized shipping box for a piece of code. It doesn't care what's inside - a Node.js app, a database, a Python script. It simply packages the code along with *everything* it needs to run, like libraries and configuration files.

> This simple idea solves one of programming's oldest headaches. A container guarantees that if the code works on a developer's machine, it will work exactly the same way in testing and production. It's the end of the "but it works on my machine!" problem.

Tools like [**Docker**](https://www.docker.com/) are the industry standard for creating these containers. Then, platforms like [**Kubernetes**](https://kubernetes.io/) step in to act as the traffic controller, automatically managing thousands of these containers across an army of servers.

### Serverless Computing: Pay Per Plate, Not for the Whole Kitchen

Serverless computing pushes the hands-off approach even further. Imagine you're catering a big event. You could rent a whole industrial kitchen for the day, paying for the space, the chefs, and the utilities whether you end up serving 10 people or 1,000. That's like managing your own servers.

Serverless is the catering company that charges you *only* for the number of plates served. You don't rent the kitchen or manage the staff; you just focus on your event, and they handle the rest.

Here's what that looks like in the cloud:

* **No Server Management:** The cloud provider takes care of all the underlying infrastructure. You never have to think about servers.
* **Pay-for-Value:** You are only billed for the exact amount of computer time your code uses, often down to the millisecond. If no one is using your app, you pay nothing.
* **Automatic Scaling:** The platform instantly scales to handle any amount of traffic, from zero requests to thousands per second, without you lifting a finger.

This model is a perfect fit for event-driven tasks, like processing a photo upload the moment it happens or handling a quick API call. It's an incredibly efficient way to build and a cornerstone of modern cloud application development.

## Choosing The Right Cloud Service Model

When you start building applications for the cloud, you'll quickly discover that "the cloud" isn't one monolithic thing. It's actually a spectrum of services packaged into different models, and each one offers a unique balance of control versus convenience. Picking the right one is a bit like deciding how you want to get a pizza: do you make it from scratch, order a take-and-bake kit, or just have a hot one delivered to your door?

This decision isn't trivial; it directly shapes your team's day-to-day responsibilities, how fast you can build and ship features, and your overall flexibility. Each model represents a trade-off. What are you willing to manage yourself, and what do you want to hand off to the cloud provider? Getting this right is the first step toward building an efficient and cost-effective application.

![Image](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/cloud-based-application-development/32d3d40d-6592-483d-88bf-4315adfc1c26.jpg)

### IaaS: The Do-It-Yourself Approach

**Infrastructure as a Service (IaaS)** is the foundational layer of cloud computing. Think of it as leasing a commercial kitchen. You get the raw space, the ovens, the plumbing, and the electricity - the basic building blocks. In cloud terms, these are the fundamental computing resources: virtual servers, raw storage, and networking components.

With IaaS, you're in the driver's seat. You get to install your preferred operating system, configure the network exactly how you want, and set up all the necessary software. This gives you maximum control, but it also means you're responsible for managing almost everything from the OS up. It's the right choice when you need a highly customized environment and have the expertise to manage it.

### PaaS: The Managed Platform

**Platform as a Service (PaaS)** is the happy medium, like getting one of those meal-prep kits. The company has already sourced the ingredients, pre-chopped the veggies, and written the recipe. All you have to do is the fun part: combine everything and cook it.

In the development world, a PaaS provider handles all the tedious backend infrastructure for you - the servers, the operating systems, the patches, and the databases. This frees up your development team to focus entirely on what they do best: writing code and building great features. PaaS dramatically accelerates the development lifecycle, which is why it's a go-to for teams looking to innovate and deploy applications quickly.

### SaaS: The Ready-to-Use Solution

**Software as a Service (SaaS)** is the most hands-off model, and it's probably the one you're most familiar with as a consumer. This is like ordering a pizza for delivery. You don't worry about the ingredients, the oven, or the cooking; you just open the box and enjoy the finished product.

Services like [Google Workspace](https://workspace.google.com/), [Dropbox](https://www.dropbox.com/), or [Salesforce](https://www.salesforce.com/) are all classic SaaS examples. The provider manages everything - the application, the data, the servers, all of it. For businesses, this means you can get powerful software up and running immediately with no development overhead, usually for a simple subscription fee.

> The core decision comes down to a trade-off: **SaaS** offers the highest convenience, **IaaS** provides the most control, and **PaaS** strikes a balance between the two, accelerating development without ceding all control.

To make this even clearer, let's break down how these three models stack up against each other.

### Comparing IaaS vs PaaS vs SaaS

The table below gives you a side-by-side look at who manages what, making it easier to see where your team's responsibilities would begin and end with each model.

| Feature | IaaS (Infrastructure) | PaaS (Platform) | SaaS (Software) |
| :--- | :--- | :--- | :--- |
| **You Manage** | Applications, Data, Runtime, Middleware, OS | Applications, Data | Nothing |
| **Provider Manages** | Virtualization, Servers, Storage, Networking | Everything in IaaS + Runtime, Middleware, OS | Everything |
| **Best For** | Total infrastructure control, custom environments | Rapid application development and deployment | End-user software, no development needed |
| **Example** | [Amazon EC2](https://aws.amazon.com/ec2/), [Microsoft Azure](https://azure.microsoft.com/en-us/products/virtual-machines) VMs | [Heroku](https://www.heroku.com/), [Google App Engine](https://cloud.google.com/appengine) | Gmail, [Slack](https://slack.com/), Netflix |

Ultimately, there's no single "best" model. The right choice depends entirely on your project's specific needs, your team's technical skills, and how much control you truly need over the underlying environment.

## A Practical Roadmap for Cloud Development

Getting a cloud application off the ground isn't a single "launch day" event; it's a journey. A disciplined approach to **cloud based application development** is what separates a secure, scalable, and cost-effective product from one that flounders. Think of it like building a house - you wouldn't just start nailing boards together without a detailed blueprint.

This roadmap breaks the entire process down into clear, manageable phases. Each stage logically builds on the one before it, guiding your team from a back-of-the-napkin idea to a fully functioning application ready for real users. Following these steps helps you sidestep common traps like budget overruns, security holes, and performance issues that can kill a project.

![Image](https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/cloud-based-application-development/2810d183-70b2-4826-9ddd-e635a466941d.jpg)

### Phase 1: Strategic Planning and Design

Before anyone writes a single line of code, you have to lay the groundwork. This initial phase is all about defining *what* you're building, *who* you're building it for, and *how* it will actually work in the cloud. It's where you make sure the technical plan serves the business goals.

Here's what happens in this phase:

* **Defining Requirements:** Get specific about the application's features, how fast it needs to be, and who will be using it.
* **Choosing an Architecture:** Will this be a collection of microservices? A serverless app? Or a more traditional monolithic structure? The answer depends on your project's complexity and how much you expect it to grow.
* **Selecting a Cloud Provider:** It's time to evaluate the big players like [AWS](https://aws.amazon.com/), [Azure](https://azure.microsoft.com/), or [GCP](https://cloud.google.com/). You'll need to compare their services, pricing, and how comfortable your team is with each platform.

Don't rush this stage. A study from the Project Management Institute found that getting the requirements wrong was a primary reason for project failure in a staggering **47%** of cases.

### Phase 2: Development and Integration

With a solid plan in hand, it's time to start building. This is where your team brings the application to life, but it requires a cloud-first mindset. Instead of coding for a single, static server, developers need to think in terms of distributed systems and automation.

A cornerstone of this phase is setting up a **CI/CD (Continuous Integration/Continuous Deployment) pipeline**. This is a system that automatically builds, tests, and deploys code changes, which makes releasing updates faster and much more reliable.

> Think of a robust CI/CD pipeline as the assembly line for modern software. It turns manual, error-prone tasks into a smooth, automated workflow, giving teams the confidence to ship new features frequently.

During this stage, your team should also lean heavily on cloud services for things like databases, user authentication, and file storage instead of trying to build them all from scratch. Tapping into the expertise of firms like **Pratt Solutions** for this can seriously speed up development and ensures you're building on battle-tested, scalable infrastructure.

### Phase 3: Rigorous Testing and Quality Assurance

Testing a cloud application is a different beast. It goes way beyond just looking for bugs. Because these systems are spread out and constantly changing, you have to confirm they perform well, are secure, and can handle things breaking.

This means multiple layers of testing are essential:

1. **Unit and Integration Testing:** Make sure the individual pieces of code and different services work together as expected.
2. **Performance and Load Testing:** Simulate a flood of users to see how the application holds up. Does it scale correctly? Does it stay responsive?
3. **Security Testing:** Actively poke and prod for vulnerabilities. This includes scanning your code and your cloud setup for any weak spots.
4. **Resilience Testing:** Sometimes you have to break things on purpose. This practice, often called chaos engineering, helps you verify that the system can recover gracefully when something inevitably goes wrong.

### Phase 4: Deployment and Operations

Once the application has passed all its tests, it's ready for deployment. In the cloud, this is rarely a one-and-done ordeal. Thanks to those CI/CD pipelines, deployments become small, frequent, and low-risk updates instead of big, stressful launch events.

After the app is live, the focus shifts to operations and monitoring. This is where cloud-native tools really shine. You need to keep a close eye on key metrics to make sure the application is running smoothly and efficiently.

Effective monitoring means watching:

* **Performance Metrics:** Things like latency (how fast it responds), error rates, and how much of your resources are being used.
* **Cost Management:** Keep a running tab on your spending to avoid any nasty surprises on your monthly bill.
* **Security Logs:** Monitor for any unusual activity that could signal an early threat.

This cycle of monitoring, learning, and iterating is what makes cloud development so effective. You get a continuous feedback loop that allows you to constantly improve the application over its entire life, making sure it always meets user needs and business goals.

## How Low-Code and No-Code Are Changing the Game
<iframe width="100%" style="aspect-ratio: 16 / 9;" src="https://www.youtube.com/embed/xZ8yYzP89e4" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

Building applications in the cloud used to be a job strictly for highly skilled developers. That world is changing fast, thanks to platforms that let just about anyone build powerful software without writing much, or any, traditional code. This is the new reality of **low-code** and **no-code** development.

Think about how website creation has evolved. A few years back, you needed a deep understanding of HTML, CSS, and JavaScript. Now, anyone can use a tool like [Squarespace](https://www.squarespace.com/) or [Wix](https://www.wix.com/) to drag and drop their way to a professional-looking site. Low-code and no-code platforms are bringing that same simplicity to business applications.

This isn't just a minor improvement; it's a fundamental shift in who gets to create software, and it's happening at an incredible speed.

### Democratizing Development
So, how does it work? Low-code and no-code platforms offer a visual environment with a library of pre-built components that take care of all the messy backend stuff. Instead of spending days writing code to build a user sign-up form or connect to a database, you can just drag a pre-made block onto a canvas and tweak its settings.

This puts the power to build directly into the hands of the people who actually understand the business problems. They're no longer waiting in line for the IT department.

* A **marketing team** can spin up a custom landing page for a new campaign in an afternoon.
* The **HR department** can build a simple app to manage vacation requests without needing developer resources.
* An **operations manager** can create a custom tool to track inventory levels in the warehouse.

This shift also frees up your professional developers. Instead of being bogged down with requests for simple forms and internal dashboards, they can focus their talent on the really hard stuff - the complex, high-value projects that demand deep coding expertise, like architecting a core API or optimizing infrastructure performance.

> This isn't about replacing developers. It's about empowering a much broader group of people to build, while letting expert engineers solve the unique, mission-critical problems that no drag-and-drop tool can handle.

### A Market Reshaping the Industry
The numbers behind this movement are staggering. These platforms have completely altered the cloud development landscape by making app creation faster and more accessible for everyone. The global market for these tools hit **USD 28.75 billion in 2024** and is projected to skyrocket to **USD 264.4 billion by 2032**. You can find even more [no-code market growth statistics on Adalo.com](https://www.adalo.com/posts/37-no-code-market-growth-statistics-every-app-builder-must-know).

This explosive growth is a clear signal that companies are grabbing onto these tools to become more agile and responsive. By removing the technical barriers, low-code and no-code are making cloud application development a faster, more inclusive process that's more tightly connected to what the business actually needs.

## So, What's Next for Cloud Application Development?

If there's one constant in cloud development, it's that nothing stays the same for long. The best practices we rely on today were just concepts a few years ago. Looking at the horizon, a few major trends are already shaping the next wave of cloud applications, pushing us beyond basic infrastructure into an era of truly intelligent, responsive, and efficient software.

Keeping an eye on these shifts isn't just about staying current; it's about building applications that will actually compete. The money trail tells the story. The market for public cloud application services, valued around **USD 245.9 million** in 2025, is projected to explode to **USD 2,024.6 million** by 2035. This massive growth is being supercharged by big leaps in AI and analytics. You can dig deeper into [the future of the public cloud market on futuremarketinsights.com](https://www.futuremarketinsights.com/reports/public-cloud-application-services-market) to see the full picture.

This kind of rapid expansion is only possible because of the powerful new capabilities being woven directly into the fabric of the cloud.

### The Rise of Integrated AI and Machine Learning

Artificial Intelligence (AI) and Machine Learning (ML) are no longer just fancy add-ons. They're becoming a core part of the development process itself. Cloud providers are embedding AI tools so deeply into their platforms that they're giving developers the power to build smarter software, faster than ever before.

This isn't just happening in one area; it's across the board:

* **AI-Assisted Coding:** Think of tools that suggest the next line of code, spot bugs before you do, or even write entire functions for you. This is happening right now and it's dramatically cutting down development time.
* **Intelligent Operations (AIOps):** We're now using AI algorithms to keep an eye on application performance, predict failures before they bring everything crashing down, and automate the kind of complex operational chores that used to require a whole team.
* **Simplified ML Model Deployment:** Cloud platforms now offer services that do the heavy lifting of training and deploying custom machine learning models. This makes advanced AI accessible to teams that don't have a small army of data scientists.

### Edge Computing Moves Processing Closer to the Action

The classic cloud model has a simple flow: data gets sent from a device to a big, central data center for processing. But for applications that need an answer *right now* - like self-driving cars or real-time factory robots - that round trip, even if it's just milliseconds, is an eternity.

**Edge Computing** completely flips that model around. It puts the processing power and data storage right where the data is being created. Instead of a sensor sending a firehose of raw data to the cloud, a small device at the "edge" of the network processes it on the spot and only sends back the important stuff. This isn't a niche idea; it's absolutely essential for the Internet of Things (IoT) and any application that can't tolerate lag.

> Edge computing isn't here to replace the cloud. Think of it as a powerful extension that enables a whole new class of real-time applications. The central cloud is still the best place for heavy-duty data analysis and long-term storage.

### FinOps Brings Financial Discipline to the Cloud

One of the cloud's biggest selling points - its incredible pay-as-you-go flexibility - can quickly become a budget nightmare. Without a watchful eye, costs can spiral out of control. This pain point has given rise to **FinOps**, which is really a cultural shift that brings financial accountability to the cloud's variable spending model.

FinOps is about more than just cutting costs. It's about making smart, data-driven decisions about where your cloud dollars are going. It gets finance, engineering, and business teams talking to each other to:

1. Keep a constant pulse on cloud usage and spending.
2. Hunt down and eliminate waste by optimizing resources.
3. Forecast future spending with a lot more confidence.

By adopting a FinOps mindset, companies make sure they're squeezing every drop of business value from their cloud investment. This kind of financial discipline is quickly becoming a non-negotiable part of any modern cloud strategy.

## Common Questions About Cloud Development
When teams start getting their hands dirty with **cloud based application development**, the theoretical concepts quickly give way to practical questions. It's one thing to read about the cloud, but it's another thing entirely to actually build on it. Let's tackle some of the most common questions that pop up when the rubber meets the road.

### What Is the Biggest Challenge in Cloud Development?
Once you get past the initial setup, two major hurdles almost always emerge: **security** and **cost management**.

Cloud security operates on a "shared responsibility model." The provider, like AWS or Azure, secures the physical data centers and the core infrastructure. But you are **100% responsible** for securing everything you build *on top* of that infrastructure. Simple misconfigurations are still a leading cause of data breaches, which makes getting your security posture right from day one absolutely essential.

At the same time, the cloud's pay-as-you-go model is both its biggest advantage and a potential pitfall. The flexibility is fantastic, but without constant vigilance, costs can balloon unexpectedly. This is why mastering both cloud security and cost governance (often called FinOps) isn't just a good idea - it's critical for any sustainable cloud strategy.

> Think of cloud resources like a running water tap. It's incredibly useful when you need it, but if you walk away and forget it's on, you'll end up with a very high bill. Active monitoring and optimization are non-negotiable.

### How Do I Choose Between AWS, Azure, and GCP?
There's no magic answer here. The "best" cloud provider is the one that best fits your project, your team's existing skills, and your company's long-term goals.

Here's a quick rundown to help you get started:

* **[Amazon Web Services (AWS)](https://aws.amazon.com/)**: As the oldest and biggest player, AWS has the most extensive menu of services. Its massive market share also means you'll find a huge community and a deep talent pool, making it a safe, solid choice for almost any project.
* **[Microsoft Azure](https://azure.microsoft.com/)**: If your organization already runs on Microsoft products, Azure is often the natural choice. It integrates beautifully with tools your team already uses, like Office 365 and Active Directory, making it a powerhouse in the enterprise world.
* **[Google Cloud Platform (GCP)](https://cloud.google.com/)**: GCP really shines in specific, high-demand areas. It's a leader in data analytics, machine learning, and container orchestration thanks to its origins with Kubernetes. If your application is data-heavy, GCP is a serious contender.

It's also worth noting that many businesses are now pursuing a multi-cloud strategy, cherry-picking the best services from different providers to avoid vendor lock-in and get the best of all worlds.

### What's the Difference Between Cloud-Based and Cloud-Native?
This is a great question because the terms sound alike but point to two fundamentally different philosophies.

Think of it this way: a **cloud-based** application is like taking an old house and moving it to a new plot of land. The house is now in a new location, but it's still the same old structure with the same old plumbing. You've simply "lifted and shifted" an existing app from your own server to run on cloud infrastructure. It works, but it wasn't designed to take full advantage of its new environment.

A **cloud-native** application, on the other hand, is like building a brand-new, modern smart home on that same plot of land. It's designed from the ground up with modern materials and technology, built to be efficient, resilient, and automated. Cloud-native apps use concepts like microservices and containers to be inherently scalable and flexible. It's not about *where* the app runs, but *how* it was built.

### Is Developing an Application in the Cloud Expensive?
Initially, no. In fact, it's usually much cheaper to get started in the cloud because you're swapping a massive upfront hardware purchase (a capital expense) for a monthly operational expense. No servers to buy, no data centers to build.

The real question is about the *ongoing* cost. This is where things can get pricey if you aren't careful. The key to keeping costs down is a proactive approach called FinOps, or cloud financial management. It's a continuous cycle of monitoring your spending, "right-sizing" your servers so you're not paying for power you don't need, using auto-scaling to handle traffic spikes efficiently, and shutting down resources when they're not in use.

With smart governance, building in the cloud is almost always more cost-effective in the long run.

---
Ready to build a scalable and secure application without the headaches of traditional infrastructure? **Pratt Solutions** specializes in delivering custom cloud-based solutions, automation, and expert technical consulting. We turn complex requirements into high-performance applications that drive real business results.

Start your project with a team that understands how to build for the cloud. [Learn more about our cloud development services](https://john-pratt.com).
