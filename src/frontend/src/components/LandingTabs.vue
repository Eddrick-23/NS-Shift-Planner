<template>
  <div class="card">
    <Tabs value="0" class="w-full overflow-hidden">
      <TabList>
        <Tab value="0" class="flex-1">Version logs</Tab>
        <Tab value="1" class="flex-1">Features</Tab>
        <Tab value="2" class="flex-1">Pro Tips</Tab>
        <Tab value="3" class="flex-1">Terms of Service</Tab>
        <Tab value="4" class="flex-1">Privacy Policy</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <div class="ml-4 mr-4">
            <h1 class="text-1xl mb-4">Version {{ versionNum }}</h1>
            <p><strong>This app is currently in beta and may be unstable.</strong></p>
            <p>
              See the
              <a
                href="https://github.com/Eddrick-23/NS-Shift-Planner/blob/main/CHANGELOG.md"
                target="_blank"
                rel="noopener noreferrer"
              >
                Changelogs
              </a>
              for more details on the latest changes.
            </p>
            <p>Read the <strong>Pro Tips</strong> for more.</p>
          </div>
        </TabPanel>
        <TabPanel value="1">
          <p class="m-0">Features</p>
        </TabPanel>
        <TabPanel value="2">
          <p class="m-0">Pro Tips</p>
        </TabPanel>
        <TabPanel value="3">
            <p> Terms of Service</p>
        </TabPanel>
        <TabPanel value="4">
            <p> Privacy Policy</p>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<script>
export default {
  name: 'LandingTabs',
  data() {
    return {
      versionNum: import.meta.env.VITE_VERSION //browser can't access modules in config.js, use VITE config
    };
  }
};
</script>
