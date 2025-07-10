
<template>
    <div class="card">
        <Tabs value="0">
            <TabList>
                <Tab value="0">Version logs</Tab>
                <Tab value="1">Header II</Tab>
                <Tab value="2">Header III</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="0">
                    <div class="ml-4 mr-4">
                        <h1 class="text-2xl mb-4">Version 1.0.1-beta</h1>
                        <p><strong>This app is currently in beta and may be unstable.</strong></p>
                        <p>
                            See the
                            <a href="https://github.com/Eddrick-23/NS-Shift-Planner/blob/main/CHANGELOG.md" target="_blank" rel="noopener noreferrer">
                                Changelogs
                            </a>
                            for more details on the latest changes.
                        </p>

                        <p>Start a new session or continue a previous session.</p>

                        <p>You can find the session ID in the <strong>bottom left</strong> of the page sidebar.</p>

                        <p>Sessions unused for <strong>24 hours</strong> or more are deleted — download as a ZIP file if needed.</p>

                        <p>Read the <strong>Pro Tips</strong> for more.</p>
                    </div>
                </TabPanel>
                <TabPanel value="1">
                    <p class="m-0">
                        Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim
                        ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Consectetur, adipisci velit, sed quia non numquam eius modi.
                    </p>
                </TabPanel>
                <TabPanel value="2">
                    <p class="m-0">
                        At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa
                        qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus.
                    </p>
                </TabPanel>
            </TabPanels>
        </Tabs>
    </div>
</template>

<script>
export default{
    name: 'LandingTabs',
}
</script>
    