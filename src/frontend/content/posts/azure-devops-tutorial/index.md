---
title: "Azure DevOps Tutorial For Modern CI/CD"
date: '2025-10-23'
description: "A practical Azure DevOps tutorial on mastering CI/CD. Learn to build pipelines, manage repos, and organize workflows with real-world examples."
draft: false
slug: '/azure-devops-tutorial'
tags:

  - azure-devops-tutorial
  - ci/cd-pipeline
  - azure-pipelines
  - devops-guide
  - azure-repos
---

![Article Header Image](https://cdn.outrank.so/fa6f58f4-0556-42c4-aa95-73bd51bc70b8/featured-image-e3befd4c-b0b1-47a4-a679-ba1028a662c1.jpg)

Alright, let's get our hands dirty and start building. This guide is all about the practical side of [Azure DevOps](https://azure.microsoft.com/en-us/products/devops), walking you through setting up your first project from scratch. We'll skip the high-level theory and focus on the real-world decisions you'll make, so you can build a solid foundation and get comfortable with the interface right away.

## Setting Up Your First Azure DevOps Project

Before you can write a line of code or build a single pipeline, you need a home for your work. In the world of Azure DevOps, this starts with an **Organization**. Think of it as the main hub for your company's development efforts or even just your personal projects. Inside that Organization, you'll create individual **Projects**.

Your first move is to create this Organization. It might seem like a simple step, but it's crucial. This is where all your source code, work items, and build artifacts will live, giving your team a single, unified space to collaborate.

### Creating Your Organization and Project

When you first sign into Azure DevOps, you'll be guided to create both your Organization and your first Project in one go. Getting this initial setup right is key to a smooth workflow later on.

The power behind this platform is, of course, Microsoft's massive cloud infrastructure. In fact, as of 2025, Microsoft Azure commands nearly **25%** of the global cloud market, with its revenue surging by **33%** in the first quarter alone. This incredible growth reflects just how many companies rely on Azure, and you can discover more insights about its market position and why it's a go-to for enterprise tools.

Here's what the project creation screen looks like - this is where you'll plug in the core details for your new workspace.

![Screenshot of the Azure DevOps project creation screen, showing fields for Project name, Description, Visibility, Version control, and Work item process.](https://cdn.outrank.so/fa6f58f4-0556-42c4-aa95-73bd51bc70b8/44426e10-eaa1-4a43-b377-2e1372afbf1f.jpg)

This screen brings together the most important choices you need to make upfront, from what you'll call your project to how you'll manage your code and track your work.

### Choosing Your Version Control and Process

During this setup, you'll hit two big decision points: **Version Control** and **Work Item Process**.

* **Version Control**: Your options are **Git** and Team Foundation Version Control (TFVC). Let me make this easy for you: for any project starting today, **always choose Git**. It's the industry standard for a reason. As a distributed system, its branching and merging capabilities are just far superior for modern development.
* **Work Item Process**: This choice dictates the vocabulary and structure for how you track work (think User Stories, Bugs, Tasks, etc.). The right one really depends on how your team likes to operate.

> For most teams just getting started, the **Agile** or **Scrum** templates are the way to go. Agile offers a great deal of flexibility, while Scrum is more structured around sprints and defined roles. My advice? Steer clear of CMMI unless you're in a highly regulated industry that explicitly requires that level of formal process and appraisal.

### Choosing Your Project Process Template

To help you decide which work item process is the best fit, here's a quick breakdown. Each template provides a different set of work item types and workflows designed to support specific development methodologies.

| Process Template | Best For | Key Work Items |
| ---------------- | ------------------------------------------------------------------------- | --------------------------------------- |
| **Agile** | Teams that need flexibility and follow methods similar to Agile. | User Story, Feature, Epic, Bug, Task |
| **Scrum** | Teams practicing Scrum who need to track product backlog items and bugs. | Product Backlog Item, Bug, Task, Epic |
| **CMMI** | Teams requiring a more formal, process-driven approach with traceability. | Requirement, Change Request, Risk, Bug |

Ultimately, the goal is to pick the template that feels most natural to your team. You want a system that helps you organize work, not one that gets in your way. For most, Agile is a perfect starting point.

## Mastering Azure Repos for Team Collaboration

Your project's source code is its lifeblood. [Azure Repos](https://azure.microsoft.com/en-us/products/devops/repos) gives it a secure, centralized home, but true source control is so much more than just `git push`. It's about building a workflow that guards code quality and keeps your main branch pristine and ready for deployment at a moment's notice.

The secret to this stability? **Branch policies**. Think of them as the automated gatekeepers for your most critical branches, like `main` or `develop`. By setting up a few simple rules, you can stop direct pushes and funnel every single change through a formal review process.

This process revolves around **pull requests**, or PRs. A PR is simply a request to merge code from a feature branch into one of those protected branches. It's the designated checkpoint where your team can review the changes, ask questions, and give a thumbs-up before the new code becomes official.

### Protecting Your Main Branch with Policies

Honestly, setting up a solid branch policy should be the very first thing you do when you start a new project. It's a five-minute task that will save you countless hours of headaches down the road.

Here are the non-negotiable policies I recommend enabling on your `main` branch from day one:

* **Require a minimum number of reviewers:** This is the big one. Setting this to at least **one** (or two for larger teams) means no code gets merged without a second pair of eyes on it. Simple as that.
* **Check for linked work items:** This policy creates an unbreakable link between your code and your project plan. It forces every PR to be associated with a User Story or Bug in [Azure Boards](https://azure.microsoft.com/en-us/products/devops/boards), so you always know *why* a change was made.
* **Check for comment resolution:** A small but powerful rule. This prevents a PR from being merged until every single comment left by a reviewer has been marked as resolved. It ensures no feedback gets ignored.

These policies create a safety net, catching mistakes and enforcing best practices automatically.

> I tell everyone to enable the "Require a minimum number of reviewers" policy, even if you're working completely alone. It forces you into the habit of reviewing your own work before merging. You'd be surprised what you catch when you take a step back and look at your code with a reviewer's mindset.

### A Real-World Pull Request Workflow

Let's see how this all comes together in a typical scenario. A developer, Alex, needs to add a new login button to the company's web app.

1. **Branch Out:** First things first, Alex creates a new local branch off `main`. He gives it a clear name, like `feature/add-login-button`, and gets to work on the code.
2. **Push and Open a PR:** Once the button is working, Alex pushes his new branch up to Azure Repos. He then hops into the web UI to create a pull request, targeting `main` from his `feature/add-login-button` branch.
3. **Connect the Dots:** On the PR screen, Alex links his work to the User Story he was assigned in Azure Boards. He then adds Maria, a senior developer on his team, as a required reviewer.
4. **The Review Cycle:** Maria gets a notification and dives into the code. She leaves a couple of comments suggesting a better way to handle a specific CSS class. Alex sees the feedback, makes the change, pushes an update, and resolves her comments. Satisfied, Maria approves the PR.
5. **Merge It:** All the gates are now green. The branch policy checks have passed: it has an approval, a linked work item, and all comments are resolved. Alex can now confidently click "Complete," and Azure Repos will merge his code into the `main` branch. The new login button is now officially part of the codebase.

## Building Your First CI/CD Pipeline

With your code tucked away safely in a repository, it's time for the real magic: automating the path from a fresh commit to a live deployment. This is the heart of what Azure DevOps does - taking your raw source code and turning it into a working application without you having to manually intervene.

We're going to walk through building a complete CI/CD pipeline for a sample .NET web application, starting with the build.

**Continuous Integration (CI)** is all about automatically building and testing your code every single time someone on the team pushes a change. This immediate feedback is a lifesaver for catching bugs early and keeping your `main` branch stable and ready to deploy at a moment's notice.

This push for rapid, reliable delivery is why the global DevOps market is exploding. It was projected to hit **$15.06 billion** in 2025, a massive leap from **$10.46 billion** in 2024. That growth tells you everything you need to know about how critical automated pipelines are in modern software. If you're curious, you can [discover more insights about the state of DevOps](https://www.baytechconsulting.com/blog/the-state-of-devops-in-2025) and see where the market is headed.

The whole process kicks off with a simple, developer-centric workflow.

![Infographic about azure devops tutorial](https://cdn.outrank.so/fa6f58f4-0556-42c4-aa95-73bd51bc70b8/145373b5-fdd5-444b-a545-a50f4c9ba642.jpg)

This three-step dance - write code, create a pull request, get it approved - is the trigger that sets our entire automated build and test cycle in motion.

### Defining Your Build with YAML

In [Azure Pipelines](https://azure.microsoft.com/en-us/products/devops/pipelines), your build process is defined as code using a YAML file that lives right inside your repository. This is what we call **Pipelines as Code**, and it's a game-changer. It means your build process is version-controlled, can be code-reviewed, and is easily reusable.

The good news is you don't have to start from scratch. When you create a new pipeline, Azure DevOps gives you a handy set of templates to get you going.

![Screenshot from https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/media/pipeline-editor-template-picker.png](https://cdn.outrank.so/fa6f58f4-0556-42c4-aa95-73bd51bc70b8/145373b5-fdd5-444b-a545-a50f4c9ba642.jpg)

Just pick a template that matches your project - like ".NET Core" in our case - and it will generate a starter `azure-pipelines.yml` file with all the standard steps for building and testing that type of application.

For our .NET web app, a basic CI pipeline will boil down to a few key stages:

* **Restore:** This step pulls down all the necessary NuGet package dependencies your project relies on.
* **Build:** Here, the C# code is compiled into DLLs and executables.
* **Test:** The pipeline automatically runs all the unit tests in your project to make sure nothing broke.
* **Publish:** Finally, it bundles all the build outputs into a single package. We call this package an **artifact**, and it's what we'll use for the actual deployment.

Every one of these steps is executed on a **build agent** - basically, a virtual machine that runs the tasks from your YAML file. You can use the convenient Microsoft-hosted agents or, for more granular control, set up your own self-hosted agents.

### Creating the Release Pipeline for Deployment

Once your CI pipeline runs successfully and produces that build artifact, it's time for **Continuous Deployment (CD)**. This is where a **Release Pipeline** comes in. Its sole job is to take that artifact and push it out to your target environments.

> While you can define deployment stages in the same YAML file, I often suggest beginners start with the classic Release Pipeline. The visual editor makes it much easier to grasp the flow from, say, a Staging environment to Production.

A smart release process rarely goes straight to production. A much safer flow involves multiple stages. For example, you'd first deploy to a Staging environment. There, you can run more in-depth automated tests or have your QA team perform manual checks before giving the green light.

### Securing Deployments with Gates and Variables

To keep deployments safe and controlled, Release Pipelines have some powerful features like **approval gates**. You can set up a rule that requires a project manager or QA lead to manually sign off before the code moves to production. This adds a critical human checkpoint to prevent an "oops" deployment.

Another must-use feature is **environment variables**. Instead of hardcoding things like database connection strings or API keys, you define them as variables for each stage. This way, your Staging environment connects to the staging database and Production connects to the live one, all from the same deployment process. It's a fundamental practice for building secure and repeatable deployments.

## Organizing Workflows with Azure Boards

A slick, automated pipeline is great, but without a solid plan behind it, it's just automation for automation's sake. That's where [Azure Boards](https://azure.microsoft.com/en-us/products/devops/boards) comes into the picture. It's the nerve center for your entire project - the place you plan sprints, manage the product backlog, track every piece of work, and give the whole team a clear view of what's happening.

![A Kanban board in Azure Boards showing columns like 'New', 'Active', 'Resolved', and 'Closed', with work item cards distributed across them.](https://cdn.outrank.so/fa6f58f4-0556-42c4-aa95-73bd51bc70b8/2a7b2603-69f7-460d-8cfe-e6c7f3e78752.jpg)

Let's walk through a real-world scenario. Say your team needs to build out a new user authentication feature. You'd start in Azure Boards by creating a **User Story** to define what the user needs. From there, you'd break that story down into smaller, bite-sized **Tasks** for the developers to tackle.

This isn't just about making lists; it's a foundational part of a healthy DevOps culture. The impact is huge. A staggering **99%** of organizations say DevOps has positively affected their operations, and **61%** directly credit it with producing higher-quality software. These aren't just my observations; you can dig into the [broader DevOps market findings](https://www.expertmarketresearch.com/reports/devops-market) to see how widespread these results are.

### Visualizing Progress with Kanban Boards

Once you have your work items, the best way to see what's going on is with a Kanban board. It gives you that crucial, at-a-glance view of your team's entire workflow.

The real magic of the Kanban board, and what makes this part of our Azure DevOps tutorial so practical, is its flexibility. You can, and absolutely should, customize the columns to mirror exactly how your team works. A common starting point looks something like this:

* **New:** All the new tasks ready to be started.
* **Active:** What a developer is currently working on.
* **Code Review:** The code is written, and a pull request is open for review.
* **Done:** The PR has been approved, merged, and the task is complete.

This kind of visualization is a lifesaver. It immediately shows you where work is piling up and helps you spot bottlenecks before they derail a sprint.

> I've seen teams get a massive boost in productivity just by adding a "Blocked" column to their board. It makes it painfully obvious what's holding things up, so everyone can jump in to find a solution. Your board should be a living tool, not a static one.

### Creating Traceability with Queries

As your project gets bigger, your boards will inevitably get crowded. That's when you need to lean on **Queries**. Think of them as custom, saved filters for your work items.

For instance, you could quickly build a query to show all high-priority bugs assigned to a particular developer that haven't been touched in the last three days. This gives managers and team leads a way to create their own dashboards and keep an eye on critical work without having to manually hunt through the backlog.

This is where you see the true power of an integrated platform. A single User Story in Azure Boards can be linked to a specific branch in Azure Repos. That branch gets tied to a pull request, which in turn triggers a build pipeline, and finally, a release. You get a complete, unbroken audit trail from the initial idea all the way to its deployment in production. It's a game-changer for traceability.

## Managing Dependencies with Azure Artifacts

<iframe width="100%" style="aspect-ratio: 16 / 9;" src="https://www.youtube.com/embed/krK4HTmaCJc" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

Let's be honest, modern applications are never built from scratch. They're assembled from countless open-source packages and internal libraries, creating a complex software supply chain. Relying solely on public registries is risky - they can go down, packages can get pulled, and security vulnerabilities can pop up without warning.

This is exactly the problem [Azure Artifacts](https://azure.microsoft.com/en-us/products/devops/artifacts) was built to solve. Think of it as your own private, secure package manager. It becomes the single source of truth for all your critical dependencies, whether they're public packages from NuGet and npm or your own shared code. By setting up a private feed, you insulate your builds from the chaos of the public internet and gain total control over what goes into your software.

Let's walk through a real-world scenario to see how this actually works in practice.

### Creating and Publishing to a New Feed

Imagine your team has built a fantastic, reusable `.NET` library for handling authentication. Multiple microservices across the company need to use it. The last thing you want is for developers to copy-paste the code, creating a maintenance nightmare.

The professional approach is to package it and publish it to a private Azure Artifacts feed.

Here's how you'd get that done:

* **Set Up Your Feed:** First, head over to the **Artifacts** section in your Azure DevOps project and create a new feed. You'll give it a clear name and set permissions for who can publish to it (contributors) and who can pull packages from it (readers).
* **Package the Library:** In your shared library's source code, you'll run the `dotnet pack` command. This compiles your code and bundles it into a neat little NuGet package, a `.nupkg` file.
* **Publish via a Pipeline:** The best part is automating the publish step. You'll add a task to your shared library's CI pipeline that authenticates with your new feed and then pushes the generated `.nupkg` file straight to it.

> Treating your internal code like a first-class package is a massive step up for code reuse. It introduces proper versioning, promotes consistency, and gives you a clear audit trail of which projects are using which version of your shared library.

### Consuming Packages in Your CI Pipeline

Great, so your custom package is now sitting securely in your feed. How do your other applications actually use it?

It's just a small configuration tweak in their CI pipelines. Inside the `azure-pipelines.yml` file for your main web application, you add a simple task to authenticate with your Azure Artifacts feed.

Once that's in place, the `dotnet restore` command in your build process automatically knows to check your private feed for that custom authentication library *before* looking at public sources like `NuGet.org`. This makes your builds far more reliable and secure, ensuring they always pull the correct, company-vetted version of every single dependency.

## Frequently Asked Questions About Azure DevOps

As you start working your way through this Azure DevOps guide, a few questions are bound to come up. It's a massive platform, after all, and figuring out the best way to use it for your specific project is key. Let's dig into some of the most common questions I hear from teams who are just getting their feet wet.

These aren't just academic questions; they're the real-world decisions and trade-offs development teams have to make every single day. Getting these answers straight early on can help you sidestep common frustrations and build good habits from the get-go.

### Azure Pipelines vs. GitHub Actions: Which One Is Right for Me?

This is probably the number one question people ask, especially since Microsoft owns both platforms. It's a great question, too. The simplest way to think about it is that they're both fantastic CI/CD tools, but they're built for different home turfs.

* **Azure Pipelines** is the native, deeply embedded CI/CD engine for the whole Azure DevOps ecosystem. If your team is already running projects on Azure Boards and storing code in Azure Repos, Pipelines creates a beautifully integrated, all-in-one workflow. It's a powerhouse, especially for enterprise teams that are all-in on the Azure cloud.

* **GitHub Actions**, on the other hand, lives and breathes inside the [GitHub](https://github.com/) platform. Its biggest win is the incredibly tight connection to the developer workflow you already know - pull requests, issues, and managing code. Plus, the community marketplace for pre-built actions is enormous, letting you automate almost anything right where your code is hosted.

So, how do you choose? It really comes down to where your team's center of gravity is. If you're managing everything inside Azure DevOps, sticking with Azure Pipelines just makes sense. If your team lives in GitHub, then GitHub Actions will feel like a much more natural extension of your process.

### Can I Really Use Azure DevOps for Free?

Cost is always a factor, especially for smaller teams, startups, or even just for a personal project you're tinkering with. I've got great news for you here: the Azure DevOps free tier is incredibly generous.

> Absolutely. You can get started with Azure DevOps and not pay a dime. The free plan is built for teams of up to **five users**, making it a perfect fit for small companies, open-source projects, and individual developers.

This isn't some watered-down trial version, either. You get access to all the core services, including unlimited private Git repos and a solid monthly allowance of CI/CD pipeline minutes on Microsoft-hosted runners. It's a zero-risk way to adopt professional-grade DevOps practices and you can always scale up later as your team and needs grow.

### Should I Use YAML or the Classic Editor for My Pipelines?

When you go to create your first pipeline, you'll see two options: the visual "Classic Editor" or a code-based YAML file. The drag-and-drop interface of the Classic Editor can seem tempting and more straightforward at first glance, but the modern, industry-standard recommendation is to go with **YAML**.

When you define your pipeline as code in an `azure-pipelines.yml` file, your entire build and release process lives right there in the repository with your application's source code. The benefits of this are massive. Your pipeline changes go through the same pull request and review process as any other code change, you can branch and experiment with your pipeline logic, and it's much easier to create reusable templates.

For any serious, long-term project, taking the time to learn the YAML syntax is an investment that will pay for itself over and over again.

---
At **Pratt Solutions**, we build and fine-tune these kinds of cloud-native CI/CD workflows every day. If you're looking for expert guidance on setting up solid DevOps practices or need a hand building custom cloud solutions, check out our [consulting services](https://john-pratt.com).
