<template>
  <div class="absolute inset-0 w-full h-full overflow-hidden z-0 pointer-events-none">
    <div class="grid grid-cols-8 gap-1 w-full h-full p-1">
      <div
        v-for="(cell, index) in cells"
        :key="cell.id"
        :class="[
          'transition-all duration-1000 ease-in-out rounded-lg',
          cell.color,
          cell.size,
          cell.opacity
        ]"
        :style="{
          transform: `translate(${cell.translateX}px, ${cell.translateY}px) scale(${cell.scale})`,
          transitionDelay: `${cell.delay}ms`
        }"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'GridShuffle',
  data() {
    return {
      cells: [],
      animationInterval: null,
      colors: [
        'bg-gray-100',
        'bg-gray-200',
        'bg-gray-300',
        
      ],
      sizes: ['w-8 h-8', 'w-12 h-12', 'w-16 h-16', 'w-6 h-6'],
      opacities: ['opacity-20', 'opacity-40', 'opacity-60']
    }
  },
  mounted() {
    this.initializeCells()
    this.startAnimation()
  },
  beforeUnmount() {
    if (this.animationInterval) {
      clearInterval(this.animationInterval)
    }
  },
  methods: {
    initializeCells() {
      // Create 64 cells (8x8 grid)
      for (let i = 0; i < 32; i++) {
        this.cells.push({
          id: i,
          color: this.getRandomColor(),
          size: this.getRandomSize(),
          opacity: this.getRandomOpacity(),
          translateX: 0,
          translateY: 0,
          scale: 1,
          delay: Math.random() * 500
        })
      }
    },
    getRandomColor() {
      return this.colors[Math.floor(Math.random() * this.colors.length)]
    },
    getRandomSize() {
      return this.sizes[Math.floor(Math.random() * this.sizes.length)]
    },
    getRandomOpacity() {
      return this.opacities[Math.floor(Math.random() * this.opacities.length)]
    },
    shuffleCells() {
      this.cells.forEach(cell => {
        // Random translation
        cell.translateX = (Math.random() - 0.5) * 100
        cell.translateY = (Math.random() - 0.5) * 100
        
        // Random scale
        cell.scale = 0.5 + Math.random() * 1.5
        
        // Occasionally change properties
        if (Math.random() < 0.3) {
          cell.color = this.getRandomColor()
        }
        if (Math.random() < 0.2) {
          cell.size = this.getRandomSize()
        }
        if (Math.random() < 0.4) {
          cell.opacity = this.getRandomOpacity()
        }
        
        // Random delay for staggered animation
        cell.delay = Math.random() * 300
      })
    },
    resetCells() {
      this.cells.forEach(cell => {
        cell.translateX = 0
        cell.translateY = 0
        cell.scale = 1
        cell.delay = Math.random() * 200
      })
    },
    startAnimation() {
      let isShuffled = false
      
      this.animationInterval = setInterval(() => {
        if (isShuffled) {
          this.resetCells()
        } else {
          this.shuffleCells()
        }
        isShuffled = !isShuffled
      }, 2000)
    }
  }
}
</script>

<style scoped>
/* Additional custom animations if needed */
.grid-cell-enter-active,
.grid-cell-leave-active {
  transition: all 0.8s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.grid-cell-enter-from,
.grid-cell-leave-to {
  opacity: 0;
  transform: scale(0);
}
</style>
